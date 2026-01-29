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


### python-yq
- jq를 포함하며, jq 문법을 그대로 따르므로 사용하기 매우 쉬움
- 전반적으로 기능도 심플해서 쓰기 편함(옵션 사용도 복잡하지 않음)
- 기본적으로 옵션없이 쓰면 즉시 yaml을 json으로 변환출력하므로, 이후 작업은 jq로 처리하면 됨.
  - jq는 C기반이라 매우 빠름
  - 최초 읽기, 최종 출력만 python-yq를 써도 훌륭함
- python, jq 등 의존성을 가진 debian 패키지가 많아서, 컨테이너 환경이나 온프레미스에서 활용시 차질 가능성
- jq를 안쓰고 yaml로써만 데이터를 다루면 느림

### go-yq

- 단일 binary로 배포가능
- Go 기반의 yaml 도구라 쿠버네티스 관련 플랫폼에서 자주 쓰이며, 점유율도 높음
- python-yq보다 빠르고, 기능이 훨씬 더 많음