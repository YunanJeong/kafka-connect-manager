"""connect.py.

kafka connect 관련 유틸모음
"""

import os
import json
import yaml
import requests
from time import sleep
from datetime import datetime

CONNECT_DEFAULT = 'localhost:8083'


class Connector:
    def __init__(self, info):
        self.info = info

    def create(self, suffix=None, connect=CONNECT_DEFAULT):
        """커넥터 생성. 커넥트가 Distributed 모드일 때 사용.

        Args:
            - suffix (bool):    커넥터 이름에 붙일 suffix
            - connect (str):    {IP}:{Port}
        """
        if suffix:
            self.info['name'] = self.info['name'] + '_' + suffix
        sleep(1)
        res = send_http(f'http://{connect}/connectors', self.info)
        print(res)
        return res

    def delete(self, connect=CONNECT_DEFAULT):
        name = str(self.info['name'])
        cmd = f'curl {connect}/connectors/{name} -XDELETE'
        os.system(cmd)

    def show(self, connect=CONNECT_DEFAULT):
        name = str(self.info['name'])
        cmd = f'curl {connect}/connectors/{name} | jq | sort'
        os.system(cmd)

    def set_name(self, name):
        self.info['name'] = name

    def get_name(self):
        return self.info['name']

    def get_config(self):
        return self.info['config']


def send_http(url, body):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    res = requests.post(url, json.dumps(body, ensure_ascii=False), headers=headers)  # NOQA
    return res


def get_yaml(filepath):
    with open(filepath, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data


def get_json(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data


def get_now():
    return datetime.today().strftime("%y%m%d")
