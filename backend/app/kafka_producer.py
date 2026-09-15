import json
import os
import logging
from kafka import KafkaProducer

logger = logging.getLogger("mlstream-kafka")

class EventProducer:
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
        self.producer = None
        self.connect()

    def connect(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=3000,
                max_block_ms=3000
            )
            logger.info(f"Successfully connected to Kafka broker at {self.bootstrap_servers}")
        except Exception as e:
            logger.warning(f"Could not connect to Kafka at {self.bootstrap_servers}: {e}. Streaming will operate in mock/log mode.")
            self.producer = None

    def send_inference_log(self, payload: dict):
        topic = "inference_logs"
        if self.producer:
            try:
                self.producer.send(topic, payload)
                self.producer.flush()
            except Exception as e:
                logger.error(f"Failed to send message to Kafka: {e}")
        else:
            logger.info(f"[KAFKA MOCK -> {topic}]: {payload}")

    def send_ground_truth(self, payload: dict):
        topic = "ground_truth_logs"
        if self.producer:
            try:
                self.producer.send(topic, payload)
                self.producer.flush()
            except Exception as e:
                logger.error(f"Failed to send message to Kafka: {e}")
        else:
            logger.info(f"[KAFKA MOCK -> {topic}]: {payload}")

event_producer = EventProducer()
