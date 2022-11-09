"""커넥터 생성."""
from lib.connect import Connector
from config.s3_sink.s3_sink_codetables import connector

con = Connector(connector)
con.create(suffix=True)
