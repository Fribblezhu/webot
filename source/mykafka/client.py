# coding:  utf-8

import time

from kafka import SimpleClient
from kafka.structs import ProduceRequestPayload
from kafka.errors import LeaderNotAvailableError
from kafka.protocol import create_message

DEFAULT_TOPIC = 'my-topic'

DEFAULT_HOSTS = ['47.97.113.212:9092']

DEFAULT_ASYNC = False

BATCH_SEND_EVERY_N = 20

BATCH_SEND_EVERY_T = 60


class MyKafkaClient:
    def __init__(self):
        self.client = SimpleClient(DEFAULT_HOSTS)

    def call_back(self, topic, partition):
        payload = ProduceRequestPayload(topic=topic, partition=partition, messages=[create_message('test call')])
        retries = 5
        reps = []
        while retries and not reps:
            retries -= 1
            try:
                reps = self.client.send_produce_request(payloads=[payload], fail_on_error=True)
            except LeaderNotAvailableError:
                self.client.load_metadata_for_topics()
                time.sleep(1)
        return reps

