[
    46, 6, 30, 34, 5, 48, 53, 43, 28, 2, 47, 15, 50, 60, 39, 24, 49, 36, 
    20, 52, 35, 25, 30, 7, 47, 9, 50, 60, 39, 24, 49, 55, 9, 59, 51
]

초기 스토리지는 위와 같고, 이걸 복호화 하는 거 같다. asm.fif 읽을 자신이 없어서 지피티 잘 돌려보면 복호화 코드를 준다. 근데 그냥 복호화 코드 제작하면 안되고 TVM의 특징을 알아야 풀 수 있는 문제이다. 

코드가 중요한 건 아니고 이부분은 걍 공부해보면 좋을 거 같아서 포스트를 좀 가져왔다. 

1. TVM은 bit-level의 데이터를 다룬다(bytes가 아니라) 하나의 cell에 최대 1023 bits : slice는 이중에서 일부 구간을 가리키는 포인터 

2. LDU/STU : TVM 초창기에는 slice copy 시에 offset alignment 누락 -> 정렬이 제대로 안 이뤄짐 

3. PUXC 연산 시 stack underflow fallback

```python 
# Fift 코드의 `set_initial_storage`에 정의된 35바이트 암호문 데이터
ENCRYPTED_PAYLOAD = bytes([
    46, 6, 30, 34, 5, 48, 53, 43, 28, 2, 47, 15, 50, 60, 39, 24, 49, 36,
    20, 52, 35, 25, 30, 7, 47, 9, 50, 60, 39, 24, 49, 55, 9, 59, 51
])

KNOWN_PREFIX = b'hspace{'

def derive_sub_keys(encrypted: bytes, plain: bytes) -> list[int]:
    sub_keys = []
    for i in range(len(plain)):
        key = encrypted[i] ^ plain[i]
        sub_keys.append(key)
    print(f"계산된 하위 키: {sub_keys}")
    return sub_keys

def decrypt_with_schedule(encrypted: bytes, key_schedule: list[int]) -> str:
    decrypted_bytes = bytearray()
    
    for i, encrypted_byte in enumerate(encrypted):
        # i % 7에 해당하는 키를 스케줄에서 선택
        key_to_use = key_schedule[i % 7]
        
        # XOR 연산을 통해 복호화
        decrypted_byte = encrypted_byte ^ key_to_use
        decrypted_bytes.append(decrypted_byte)
        
    # 바이트 배열을 UTF-8 문자열로 디코딩하여 반환
    return decrypted_bytes.decode('utf-8', errors='ignore')

# --- 메인 실행 로직 ---
if __name__ == "__main__":

    # 1. 'hspace{' 접두사를 이용해 복호화에 필요한 7개의 하위 키(스케줄)를 알아냅니다.
    key_schedule = derive_sub_keys(ENCRYPTED_PAYLOAD, KNOWN_PREFIX)
    
    # 2. 알아낸 키 스케줄을 사용하여 전체 암호문을 복호화합니다.
    #    이 과정은 Fift 코드의 REPEAT 루프와 완전히 동일한 로직입니다.
    flag = decrypt_with_schedule(ENCRYPTED_PAYLOAD, key_schedule)
    
    print("\n" + "="*40)
    print(f"FLAG: {flag}")
```