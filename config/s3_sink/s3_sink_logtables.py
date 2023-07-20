"""S3 Sink Connector."""

topics = "kst_logtable0, kst_logtable1, kst_logtable2"
s3_bucket = 'my-bucket'
s3_dir = "my-dir"
connector_name = "s3_sink_logtables"

connector = {
    "name": connector_name,
    "config": {
        "connector.class": "io.confluent.connect.s3.S3SinkConnector",
        "storage.class": "io.confluent.connect.s3.storage.S3Storage",
        "format.class": "io.confluent.connect.s3.format.json.JsonFormat",

        "tasks.max": 4,                            # 한 토픽의 파티션 수 만큼 지정(토픽 수 아님)
        "topics": topics,

        "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",  # NOQA
        "path.format": "'year'=YYYY/'month'=MM/'day'=dd",
        "partition.duration.ms": "86400000",       # Daily S3 Partition
        "locale": "ko_KR",
        "timezone": "Asia/Seoul",
        "timestamp.extractor": "RecordField",      # Event Time 기준 S3 Partition
        "timestamp.field": "RegDate",

        "rotate.schedule.interval.ms": "1800000",  # 30분마다 새 파일 업로드
        "flush.size": 100000,

        "s3.region": "ap-northeast-2",
        "s3.bucket.name": s3_bucket,
        "topics.dir": s3_dir,
        "s3.compression.type": "gzip",

        # JsonConverter에서 스키마 미사용하기
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": False

        # Record의 Key 부분이 있다면, 별도로 처리해줘야 한다.
        # Record의 Key,Value 둘 다 한 파일에 저장은 기본지원하지 않는다. (커스텀 SMT나 Streams 등으로 별도 편집필요)
        # key.converter: org.apache.kafka.connect.converters.ByteArrayConverter
        # store.kafka.keys: true                                             # Record의 Key도 별도 파일로 저장하기
        # keys.format.class: io.confluent.connect.s3.format.json.JsonFormat  # Record의 Key 출력파일의 형식 지정
        
    }
}