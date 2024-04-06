import io
import json
import os
import urllib.parse
from collections import defaultdict
from datetime import datetime

import boto3
from loguru import logger
from pypika import Query, Table
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

metrices = [
    "mem_used_percent",
    "cpu_usage_iowait",
    "cpu_usage_idle",
    "cpu_usage_system",
    "diskio_reads",
    "cpu_usage_user",
    "disk_used_percent",
    "swap_used_percent",
]

s3 = boto3.client("s3")

db_username = os.getenv("DB_USERNAME", "postgres")
db_password = os.getenv("DB_PASSWORD", "password")
db_host_name = os.getenv("DB_HOST_NAME", "localhost")
db_name = os.getenv("DB_NAME", "cost_wiz")
db_port = 5432

db_url = f"postgresql+psycopg2://{db_username}:{db_password}@{db_host_name}:{db_port}/{db_name}"

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)


def parse_data(data):

    metric_name = data["metric_name"]

    if metric_name in metrices:
        instance_id = data["dimensions"]["InstanceId"]
        timestamp = data["timestamp"]

        value = data["value"]
        _max = value["max"]
        _min = value["min"]

        return metric_name, instance_id, timestamp, _max, _min


table = Table("instance_stats")

logger.info("Ok")


def handler(event, context):
    logger.info("Started")

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"], encoding="utf-8")

    # bucket = "metricstreams-quickpartial-a1wumz-krp6kg1o"
    # key = "2024/04/05/20/MetricStreams-QuickPartial-A1Wumz-WPP6CaZj-1-2024-04-05-20-00-27-db6a5744-6596-4245-ad04-17da1d9acba0"
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        data = response["Body"].read().decode("utf-8")

        data_to_insert = defaultdict(dict)

        with io.StringIO() as in_memory_file:
            in_memory_file.write(data)

            in_memory_file.seek(0)

            lines = in_memory_file.readlines()

            for line in lines:
                parsed = json.loads(line)
                parsed_data = parse_data(parsed)
                if parsed_data:
                    metric_name, instance_id, timestamp, _max, _min = parsed_data
                    data_to_insert[timestamp][f"{metric_name}_max"] = _max
                    data_to_insert[timestamp][f"{metric_name}_min"] = _min
                    data_to_insert[timestamp]["instance_id"] = instance_id
                    data_to_insert[timestamp]["timestamp"] = datetime.fromtimestamp(timestamp / 1000)

        data = data_to_insert.values()

        conn = engine.connect()

        for d in list(data):
            insert_query = Query.into(table).columns(*d.keys()).insert(*d.values()).get_sql()
            conn.execute(text(insert_query))

        conn.commit()

        conn.close()

        logger.info("End")
    except Exception as e:
        logger.error(e)
