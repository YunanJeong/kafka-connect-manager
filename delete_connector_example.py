"""코드테이블 커넥터 일괄 삭제."""
import os
from lib.connect import Connector, get_yaml

WORK_DIR = os.getcwd()
FILEPATH = f'{WORK_DIR}/config/jdbc_src/jdbc_src_codetables.yml'

file = get_yaml(FILEPATH)
infos = file['connectors']

# 커넥터 정보로 삭제
date = '221025'
for info in infos:
    con = Connector(info)
    con.set_name(con.get_name() + '_' + date)
    print(con.get_name())
    # con.delete()

# 커넥터 이름으로 삭제
#date = '221025'
#info = {"name": f"jdbc_src_tablename_{date}"}
#con = Connector(info)
# con.delete()