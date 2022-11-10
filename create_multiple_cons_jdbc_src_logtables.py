"""코드테이블 커넥터 일괄 생성."""
import os
import lib.broker as broker
from lib.connect import Connector, get_yaml, get_json


WORK_DIR = os.getcwd()
file = get_yaml(f'{WORK_DIR}/config/jdbc_src/jdbc_src_logtables.yml')
jdbc_info = get_json(f'{WORK_DIR}/config/jdbc_src/jdbc_info.json')
infos = file['connectors']
common = file['common']

# jdbc 연결 정보를 공통사항에 반영
common['config'].update(jdbc_info)

# 공통사항을 모든 커넥터 정보에 반영
for info in infos:
    info['config'].update(common['config'])

# 커넥터 생성
for info in infos:
    con = Connector(info)
    broker.create_topic(topic=con.get_topic_prefix(), partitions=4)  # NOQA
    con.create(suffix=True)
    # print(con.get_name())
    # print(con.get_config())

