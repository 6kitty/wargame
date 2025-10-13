#!/usr/bin/env python3
from pwn import *
from collections import Counter
import re

class RemoteWordleSolver:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.conn = None
        self.all_words = self.load_words()
        self.reset_game_state()

    def load_words(self):
        """words.txt 파일에서 모든 5글자 단어를 로드합니다."""
        try:
            with open('words_small.txt', 'r') as f:
                words = sorted(list(set(word.strip().lower() for word in f if len(word.strip()) == 5)))
            if not words: raise FileNotFoundError
            log.info(f"Loaded {len(words)} words from words.txt")
            return words
        except FileNotFoundError:
            log.warning("words.txt not found. Using a small default list.")
            return sorted(['arose', 'slate', 'crane', 'raise', 'audio', 'adieu', 'pizza', 'dizzy'])

    def reset_game_state(self):
        """라운드 시작 시 모든 상태를 초기화합니다."""
        self.candidates = self.all_words[:]
        self.green_blocks = {}
        self.yellow_blocks = {}
        self.min_counts = Counter()
        self.exact_counts = {}
        self.gray_letters = set()  # [추가] 확실히 없는 글자 기록
        self.attempt = 0

    def connect(self):
        self.conn = remote(self.host, self.port)
        log.info("Connected to server")

    def parse_feedback(self, response_bytes):
        """정규 표현식을 사용하여 ANSI 색상 코드를 순차적으로 파싱합니다."""
        text = response_bytes.decode(errors='ignore')
        ansi_pattern = re.compile(r'\x1b\[(\d+)m([^\x1b]+)')
        matches = ansi_pattern.findall(text)
        
        verdicts = []
        for code_str, char_segment in matches:
            if not char_segment.strip(): continue
            code = int(code_str)
            verdict = 'GRAY'
            if code == 32: verdict = 'GREEN'
            elif code == 33: verdict = 'YELLOW'
            
            for char in char_segment:
                if char.isalpha() and len(verdicts) < 5:
                    verdicts.append(verdict)
        return verdicts

    def update_constraints(self, word, verdicts):
        """중복 글자 피드백을 정확하게 처리하고, gray_letters를 업데이트합니다."""
        guess_counts = Counter(word)
        
        current_min_counts = Counter()
        for i, (letter, verdict) in enumerate(zip(word, verdicts)):
            if verdict == 'GREEN':
                self.green_blocks[i] = letter
                current_min_counts[letter] += 1
            elif verdict == 'YELLOW':
                if i not in self.yellow_blocks: self.yellow_blocks[i] = set()
                self.yellow_blocks[i].add(letter)
                current_min_counts[letter] += 1
        
        for letter, count in current_min_counts.items():
            self.min_counts[letter] = max(self.min_counts[letter], count)

        for letter, count in guess_counts.items():
            if count > self.min_counts[letter]:
                self.exact_counts[letter] = self.min_counts[letter]
                # [수정] Green/Yellow가 아닌 글자는 gray_letters에 추가
                if self.min_counts[letter] == 0:
                    self.gray_letters.add(letter)

    def matches_constraints(self, word):
        """단어가 모든 제약 조건을 정확히 만족하는지 확인합니다."""
        word_counts = Counter(word)
        for pos, letter in self.green_blocks.items():
            if word[pos] != letter: return False
        for pos, letters in self.yellow_blocks.items():
            if word[pos] in letters: return False
        for letter, count in self.exact_counts.items():
            if word_counts[letter] != count: return False
        for letter, count in self.min_counts.items():
            if letter not in self.exact_counts and word_counts[letter] < count:
                return False
        # [추가] gray_letters 제약 조건 추가
        if any(gl in word for gl in self.gray_letters):
            return False
        return True

    def pick_word(self):
        """다음 시도할 단어를 선택합니다. 첫 시도는 'raise'로 고정됩니다."""
        if self.attempt == 0:
            return 'raise'
        
        self.candidates = [w for w in self.candidates if self.matches_constraints(w)]
        
        if not self.candidates:
            return None
        if len(self.candidates) == 1:
            return self.candidates[0]
        
        freq_map = Counter("".join(self.candidates))
        best_word, best_score = "", -1
        for word in self.candidates:
            score = sum(freq_map[c] for c in set(word))
            if score > best_score:
                best_score = score
                best_word = word
        return best_word

    def solve_round(self):
        """한 라운드를 해결합니다. 지능적 추론 실패 시 브루트포스로 전환합니다."""
        for self.attempt in range(1, 7):
            guess = self.pick_word()
            
            if guess is None:
                log.warning("No candidates left! Switching to Brute-Force mode.")
                # --- [수정됨] 브루트포스 로직 시작 ---
                
                # 1. 브루트포스 후보 목록 생성
                # - 회색 글자 제외
                # - 초록색 위치 제약 조건 만족
                brute_force_list = [
                    w for w in self.all_words 
                    if not any(gl in w for gl in self.gray_letters) and \
                       all(w[pos] == letter for pos, letter in self.green_blocks.items())
                ]

                # 2. 우선순위 정렬 (노란색/초록색 글자를 많이 포함할수록 높음)
                required_letters = set(self.min_counts.keys())
                brute_force_list.sort(
                    key=lambda w: sum(1 for char in required_letters if char in w),
                    reverse=True
                )
                
                log.info(f"Starting brute-force with {len(brute_force_list)} words (required: {required_letters}, grayed: {self.gray_letters})")
                
                # 3. 남은 시도 동안 브루트포스 실행
                for bf_guess in brute_force_list:
                    if self.attempt >= 7: break

                    log.info(f"Brute-Force Attempt {self.attempt}: Guessing '{bf_guess}'")
                    self.conn.recvuntil(b'Enter your guess:')
                    self.conn.sendline(bf_guess.encode())
                    response = self.conn.recvline(timeout=5)

                    if b'Correct!' in response:
                        log.success(f"Solved in brute-force! The word was '{bf_guess}'.")
                        return True
                    
                    self.attempt += 1 # 시도 횟수 수동 증가
                return False # 브루트포스도 실패

            # --- 일반 로직 계속 ---
            log.info(f"Attempt {self.attempt}: Guessing '{guess}' ({len(self.candidates)} candidates left)")
            self.conn.recvuntil(b'Enter your guess:')
            self.conn.sendline(guess.encode())
            response = self.conn.recvline(timeout=5)
            
            if b'Correct!' in response:
                log.success(f"Solved! The word was '{guess}'.")
                return True
            
            verdicts = self.parse_feedback(response)
            if len(verdicts) != 5:
                log.error("Failed to parse feedback.")
                return False
            
            self.update_constraints(guess, verdicts)
        
        log.error("Failed to solve in 6 attempts")
        return False

    def solve_multiple_rounds(self, target_rounds=100):
        """100 라운드 전체를 해결합니다."""
        self.connect()
        try: self.conn.recvuntil(b'Round 1', timeout=5)
        except EOFError: log.error("Connection failed."); return
        
        for round_num in range(1, target_rounds + 1):
            log.info(f"{'='*20} Round {round_num} {'='*20}")
            if round_num > 1:
                try: self.conn.recvuntil(f"Round {round_num}".encode(), timeout=5)
                except EOFError: log.error("Connection lost."); break
            
            self.reset_game_state()
            if not self.solve_round():
                log.error(f"Failed to solve round {round_num}. Aborting."); break
        
        log.success("All rounds should be cleared! Trying to get the flag...")
        try:
            flag = self.conn.recvall(timeout=3)
            log.success(f"Flag: {flag.decode(errors='ignore')}")
        except EOFError:
            log.info("Connection closed by server after solving.")
        self.conn.close()

if __name__ == '__main__':
    HOST = 'host'
    PORT = port
    solver = RemoteWordleSolver(HOST, PORT)
    solver.solve_multiple_rounds()
