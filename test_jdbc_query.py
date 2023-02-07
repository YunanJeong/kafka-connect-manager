"""DB관리툴 대신 kafka jdbc connector로 1회성 쿼리 테스트 하기"""
import os
import lib.broker as broker
from lib.connect import Connector, get_yaml, get_json
from time import sleep

WORK_DIR = os.getcwd()
file = get_yaml(f'{WORK_DIR}/config/0_test/jdbc_query.yml')
jdbc_info = get_json(f'{WORK_DIR}/config/jdbc_src/jdbc_info.json')
infos = file['connectors']

common = {
    "config": {
      "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
      "tasks.max": "1",
      "db.timezone": "Asia/Seoul",
      "value.converter": "org.apache.kafka.connect.json.JsonConverter",
      "value.converter.schemas.enable": False,
      "numeric.mapping": "best_fit",

      # 일회성 쿼리 결과를 보기 위한 옵션
      #"topic.prefix": "",
      "mode": "bulk",
      "poll.interval.ms": 100000,  # default: 5000ms
      "batch.max.rows": 2000,      # default: 100개
    }
}
# jdbc 연결 정보를 공통사항에 반영
common['config'].update(jdbc_info)

# 공통사항을 모든 커넥터 정보에 반영
for info in infos:
    info['config'].update(common['config'])
    info['config']['topic.prefix']=info['name']

# 테스트용 토픽 및 커넥터 생성
for info in infos:
    con = Connector(info)
    topic = con.get_config()['topic.prefix']
    broker.create_topic(topic=topic, partitions=1)  # NOQA
    con.create()

sleep(2)
sleep(3)  # 국외->국내라서 조금 더 오래걸림

# 테스트 결과 출력, 커넥터 삭제, 토픽 삭제
for info in infos:
    con = Connector(info)
    topic = con.get_config()['topic.prefix']
    broker.show_records(topic=topic)
    con.delete()
    broker.delete_topic(topic=topic)
