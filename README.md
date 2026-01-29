# kafka-connect-manager
- kafka connect에서 connector를 생성, 삭제, 관리하기 위한 라이브러리.
- 실사용시 편의성을 고려하여 조금씩 개선해나간다.



yq (jq와 비슷한 yaml 처리 도구)
POST 대신 PUT
  - 운영관점에서 PUT이 나음 (등록 및 업데이트)
  - 커넥터 config 기술 방식도 간단해짐
쉘스크립트 단일파일로 관리
  - 다양한 환경에서 빠르게 쓰기 쉬움




sudo snap install yq
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq &&\
    chmod +x /usr/local/bin/yq


