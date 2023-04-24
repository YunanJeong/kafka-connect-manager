"""로그테이블 커넥터 일괄 생성."""
import os
import sys
import lib.broker as broker
from lib.connect import Connector, get_yaml, get_json


def main(file):
    infos = file['connectors']
    common = file['common']

    # 공통사항을 모든 커넥터 정보에 반영
    for info in infos:
        info['config'].update(common['config'])
    print(infos)
    # 커넥터 생성
    for info in infos:
        con = Connector(info)
        # broker.create_topic(topic=con.get_config()['topic.prefix'], partitions=con.get_config()['tasks.max'])  # NOQA
        con.create()
        # print(con.get_name())
        # print(con.get_config())


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("커넥터 설정파일 인자 필요")
        sys.exit()
    filepath = sys.argv[1]
    file = get_yaml(filepath)
    main(file)