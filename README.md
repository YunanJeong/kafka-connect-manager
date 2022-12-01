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
    - Consumer가 어떤 topic에 대해 `어디까지 읽었는지(consume)`, `broker side에 표기(commit)`해두는 것이다.
    - topic 별, consumer group 별, partition 별로 기록 된다.
    - offset정보의 실제저장경로는 `server.properties의 log.dir 설정경로(kafka-logs)`이다.
    - topic 삭제시 관련 offset도 삭제된다.

## Source connector를 위한 connect_offsets 다루기
- Source Connector는 Producer이다.
- Kafka의 offset은 Consumer를 위한 것이므로, connect_offsets라는 개별토픽이 생성되어 Source Connector를 위한 offset 관리가 수행된다. Source Connector가 `어디까지 Push했는지(produce)`, `broker side의 topic 'connect_offsets' 에 표기`해두는 것이다.

- Source Connector는 topic을 삭제해도 offset이 남아있다.
    - 커넥터 이름을 변경하면 초기화된 것 처럼 사용할 수 있다.

- 각 Source Connector에 대한 offset이 각 Partition에 저장(커밋)된다.
- 다음 커맨드를 통해 Partiton 넘버를 찾을 수 있다.
kafkacat -b localhost:9092 -t connect-offsets -e -q -f'Key:%k Partitions: %p \n' | sort -u
```
Key:["jdbc_src_1",{"query":"query"}]    Partitions: 5
Key:["jdbc_src_2",{"query":"query"}]    Partitions: 14
Key:["jdbc_src_3",{"query":"query"}]    Partitions: 5
Key:["jdbc_src_4",{"query":"query"}]    Partitions: 14
Key:["jdbc_src_5",{"query":"query"}]    Partitions: 17
Key:["jdbc_src_6",{"query":"query"}]    Partitions: 4
Key:["jdbc_src_7",{"query":"query"}]    Partitions: 12
```

- 다음 커맨드처럼 json형식으로 기술해서 jq를 쓸 수도 있다.
```
kafkacat -b localhost:9092 -t connect-offsets -e -q -f'{"Key": %k , "Payload": %s, "Partition": %p,  "Offset": %o }\n'  | jq
```
```
- f: 문자열
- %o: offset넘버
- %k: payload. jdbc Source Connector의 경우, record의 value자리에 incrementing key 또는 timestamp key 값이 입력된다. bulk모드일때는 해당 값이 비어있으므로 json이 위 처럼 쓰면 json이 깨진다.
```

- Source Connector가 다음 데이터를 읽을 때는, 해당 Partition의 "최신값"만을 참조한다.
	- 따라서 offset을 조작하고싶을 때 offset 넘버는 순차대로 늘려주되 payload 값을 조정하면 된다.

# Key-value 포맷 확인
kafkacat -b localhost:9092 -t connect-offsets -e -q -K###

# 원하는 Key-value 입력해서 produce
echo '["{connector_name}", {"query":"query"}]###' | kafkacat -b localhost:9092 -t connect-offsets -P -Z -K### -p {partition}

```
$ echo '["jdbc_src_1",{"query":"query"}]#{"incrementing":369034}' | kafkacat -b localhost:9092 -t connect-offsets -P  -K# -p 6
$ echo '["jdbc_src_2",{"query":"query"}]#{"incrementing":144617150}' | kafkacat -b localhost:9092 -t connect-offsets -P  -K# -p 22
$ echo '["jdbc_src_3",{"query":"query"}]#{"timestamp_nanos":817000000,"timestamp":1669701595817}' | kafkacat -b localhost:9092 -t connect-offsets -P  -K# -p 14
```