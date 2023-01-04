"""broker.py.

kafka broker 관련 유틸모음
"""

import os

KAFKA_HOME = '/usr/local/kafka'
BROKER_DEFAULT = 'localhost:9092'


def create_topic(topic, partitions, replications=1,
                 broker=BROKER_DEFAULT):
    """커넥터 생성. 커넥트가 Distributed 모드일 때 사용.

    Args:
        - topic (str):         토픽명
        - partitions (int):    파티션 수
        - replications (int):  리플리케이션팩터 수
        - broker (str):        {IP}:{Port}, (default:localhost:9092)

    Note:
        - 토픽 생성. 이미 토픽이 존재하면 에러만 출력 후 변화없음.
    """
    cmd = f'{KAFKA_HOME}/bin/kafka-topics.sh' \
        + f' --create --topic {topic}' \
        + f' --bootstrap-server {broker}' \
        + f' --partitions {partitions} --replication-factor {replications}'
    os.system(cmd)


def delete_topic(topic, broker=BROKER_DEFAULT):
    """토픽 삭제. 사용 주의."""
    # server.properties에 delete.topic.enable=true 필요 (default)
    cmd = f'{KAFKA_HOME}/bin/kafka-topics.sh' \
        + f' --bootstrap-server {broker}' \
        + f' --topic {topic} --delete'
    os.system(cmd)


def show_topics(broker=BROKER_DEFAULT):
    cmd = f'kafkacat -b {broker} -L | grep topic'
    os.system(cmd)


def show_records(topic, broker=BROKER_DEFAULT):
    cmd = f'kafkacat -b {broker} -t {topic} -q -e'
    os.system(cmd)


def test_function():
    print('test')