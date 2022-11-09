# kafka-connect-manager
- kafka connect에서 connector를 생성, 삭제, 관리하기 위한 라이브러리.
- 실사용시 편의성을 고려하여 조금씩 개선해나간다.

## requirement
- `sudo apt install kafkacat`
- `sudo apt install jq`

## 디렉토리
"""
├── config/                                       # 커넥터 설정 파일 예제
├── create_multiple_cons_jdbc_src_codetables.py   # example: jdbc connector 여러 개 등록
├── create_multiple_cons_jdbc_src_logtables.py    # example: jdbc connector 여러 개 등록
├── create_s3_sink_codetables.py                  # example: 여러 topic을 참조하는 s3 connector 1개 등록
├── create_s3_sink_logtables.py                   # example: 여러 topic을 참조하는 s3 connector 1개 등록
├── delete_connector_example.py                   # example: 토픽 삭제
└── lib/                                          # connect, broker 명령어 라이브러리 모음
"""

## 커넥터 설정 파일
- broker 및 connect에 REST api로 동작명령을 전달할 수 있다.
- 다수 커넥터 관리를 위해 **메시지 전달 기능(`lib/`)과 커넥터 설정 내용(`config/`)을 분리**하여 관리할 필요가 있다.

- 커넥터 설정 파일 형식
    - json: kafka 기본 사용 형식
    - yaml:
        - json과 달리 **주석쓰기 좋다**. 더 자유로운 형식.
        - 다수 커넥터를 한 파일에 기술하고, 공통부분을 묶어 관리하기 좋다.
    - py:
        - 커넥터 설정 파일을 py로 작성하고, 이후 import하여 사용할 수 있다.
        - 로직이 필요한 경우 편하다.
        ```
        - e.g.) 다수 jdbc source connector의 query 옵션에서 동일한 SQL문을 써야하는데, 대상 테이블만 많은 상황
        - 이 때 python 로직으로 공통 SQL문 작성 후, 테이블명만 할당하면 편하다.
        - yml에서도 가능하지만, python이 더 직관적
        ```
