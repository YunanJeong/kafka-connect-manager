# kafka-connect-manager
- kafka connect에서 connector를 생성, 삭제, 관리하기 위한 라이브러리.
- 실사용시 편의성을 고려하여 조금씩 개선해나간다.

## requirement
- `$ sudo apt install kafkacat`
- `$ sudo apt install jq`

## 디렉토리
```
├── config/                                       # 커넥터 설정 파일 예제
├── create_multiple_cons_jdbc_src_codetables.py   # example: jdbc connector 여러 개 등록
├── create_multiple_cons_jdbc_src_logtables.py    # example: jdbc connector 여러 개 등록
├── create_s3_sink_codetables.py                  # example: 여러 topic을 참조하는 s3 connector 1개 등록
├── create_s3_sink_logtables.py                   # example: 여러 topic을 참조하는 s3 connector 1개 등록
├── delete_connector_example.py                   # example: 토픽 삭제
└── lib/                                          # connect, broker 명령어 라이브러리 모음
```

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

## broker 모듈 간단히 쓰기
```
$ python
>>> import broker
>>> broker.show_topics()               # kafkacat, grep 내부 사용
>>> broker.delete_topic('topic_name')  # kafka shell 내부 사용
...
```

## Sink Connector를 위한 offset 다루기
- Sink Connector는 Consumer이므로, broker에서 일반적인 offset으로 취급, 관리된다.
- offset
    - Consumer가 어떤 topic에 대해 `몇 번째 데이터까지 읽었는지(consume)`, `Broker side에 표기(commit)`해두는 것이다.
    - topic 별, consumer group 별, partition 별로 기록 된다.
    - offset정보의 실제저장경로는 `server.properties의 log.dir 설정경로(kafka-logs)`이다.
    - topic 삭제시 관련 offset도 삭제된다.

## Source connector를 위한 connect_offsets 다루기
- Source Connector는 Producer이기 때문에 Kafka의 일반 offset관리와는 별도 수행된다.
- Source Connector의 offset은 connect_offsets라는 별도 Topic에 저장된다. Source Connector가 `몇 번째 데이터까지 Broker로 Push했는지(produce)`, `Broker의 Topic 'connect_offsets'에 표기`해두는 것이다.
- **Source Connector는 `connect_offsets에서 최신 offset의 Record만 참조`하여, 자신이 어디까지 데이터를 읽었는지 판단한다.**
### connect_offsets의 Record 구조
    - Headers: 파티션 넘버, 오프셋 넘버, ...
    - Body:
        - key: 커넥터 이름
        - value: 어느 데이터까지 읽었는지 표기 (jdbc의 경우 incrementing key, timestamp key가 저장됨)


### Source Connector의 offset 유지 방법
    - 같은 커넥터명으로 삭제, 수정, 등록

### Source Connector의 offset 초기화 방법 [[1]](https://rmoff.net/2019/08/15/reset-kafka-connect-source-connector-offsets/) [[2]](https://soojong.tistory.com/entry/Source-Connector-Offset-%EC%B4%88%EA%B8%B0%ED%99%94-%ED%95%98%EA%B8%B0)
    1. 다른 커넥터명으로 새로 등록
        - 이 경우, 기존 커넥터명으로 저장된 offset은 계속 남아있다!
    2. 또는 connect_offsets에 새로운 값을 입력



## connect_offsets 수정시 자주 쓰는 커맨드
1. 커넥터 이름 별 offset이 저장되는 Partiton 넘버 찾기
- `$ kafkacat -b localhost:9092 -t connect-offsets -e -q -f'Key:%k Partitions: %p \n' | sort -u`
    ```
    Key:["jdbc_src_1",{"query":"query"}]    Partitions: 5
    Key:["jdbc_src_2",{"query":"query"}]    Partitions: 14
    Key:["jdbc_src_3",{"query":"query"}]    Partitions: 5
    Key:["jdbc_src_4",{"query":"query"}]    Partitions: 14
    Key:["jdbc_src_5",{"query":"query"}]    Partitions: 17
    Key:["jdbc_src_6",{"query":"query"}]    Partitions: 4
    Key:["jdbc_src_7",{"query":"query"}]    Partitions: 12
    ```

2. 다음 커맨드처럼 json형식으로 기술해서 jq를 쓸 수도 있다.
    ```
    $ kafkacat -b localhost:9092 -t connect-offsets -e -q -f'{"Key": %k , "Payload": %s, "Partition": %p,  "Offset": %o }\n'  | jq
    ```
    ```
    - f: 문자열
    - %o: offset넘버
    - %k: payload. jdbc Source Connector의 경우, record의 value자리에 incrementing key 또는 timestamp key 값이 입력된다. bulk모드일때는 해당 값이 비어있으므로 json이 위 처럼 쓰면 json이 깨진다.
    ```

3. Key-value 포맷 확인
    - `kafkacat -b localhost:9092 -t connect-offsets -e -q -K###`

4. 원하는 Key-value 입력해서 produce하여 offset 조작
    - `echo '["{connector_name}", {"query":"query"}]###' | kafkacat -b localhost:9092 -t connect-offsets -P -Z -K### -p {partition}`

    ```
    # jdbc_src_1 커넥터는 369034번 데이터까지 읽은 것으로 수정
    echo '["jdbc_src_1",{"query":"query"}]#{"incrementing":369034}' | kafkacat -b localhost:9092 -t connect-offsets -P  -K# -p 5

    # jdbc_src_2 커넥터는 144617150번 데이터까지 읽은 것으로 수정
    echo '["jdbc_src_2",{"query":"query"}]#{"incrementing":144617150}' | kafkacat -b localhost:9092 -t connect-offsets -P  -K# -p 14

    # jdbc_src_3 커넥터는 1669701595817번 데이터까지 읽은 것으로 수정
    echo '["jdbc_src_3",{"query":"query"}]#{"timestamp_nanos":817000000,"timestamp":1669701595817}' | kafkacat -b localhost:9092 -t connect-offsets -P  -K# -p 5
    ```

