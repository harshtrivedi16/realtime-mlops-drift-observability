import json
import os
import logging
import threading
import time
from kafka import KafkaConsumer
from app.drift_engine import drift_engine
from app.metrics import DRIFT_SCORE, IS_DRIFTING, RETRAIN_COUNT
from app.models.model import model_service

logger = logging.getLogger("mlstream-kafka-consumer")

class EventConsumer(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.bootstrap_servers = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
        self.consumer = None
        self.running = False
        self.last_retrain_time = 0

    def connect(self):
        try:
            self.consumer = KafkaConsumer(
                "inference_logs",
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id="drift-analyzer-group",
                auto_offset_reset="latest",
                session_timeout_ms=6000,
                heartbeat_interval_ms=2000
            )
            logger.info(f"Kafka Consumer connected to {self.bootstrap_servers}")
        except Exception as e:
            logger.warning(f"Could not connect Kafka Consumer: {e}. Running in Mock Consumer mode.")
            self.consumer = None

    def run(self):
        self.running = True
        for _ in range(5):
            self.connect()
            if self.consumer:
                break
            time.sleep(2)

        if not self.consumer:
            logger.info("Starting Mock Consumer Loop (No Kafka)")
            self._mock_loop()
        else:
            logger.info("Starting Kafka Consumer Loop")
            self._kafka_loop()

    def _kafka_loop(self):
        while self.running:
            try:
                records = self.consumer.poll(timeout_ms=1000)
                for topic_partition, messages in records.items():
                    for message in messages:
                        self.process_message(message.value)
            except Exception as e:
                logger.error(f"Error in Kafka consumer loop: {e}")
                time.sleep(2)

    def _mock_loop(self):
        while self.running:
            time.sleep(1)

    def process_message(self, payload: dict):
        features = payload.get("features")
        if features:
            drift_engine.add_sample(features)
            
            # Recalculate drift and update Prometheus
            drift_res = drift_engine.calculate_drift()
            
            DRIFT_SCORE.set(drift_res["drift_score"])
            is_drift = drift_res["is_drifting"]
            IS_DRIFTING.set(1 if is_drift else 0)

            # Automated Retraining Alert Logic: If drift > threshold and cooldown passed (30s)
            current_time = time.time()
            if is_drift and (current_time - self.last_retrain_time > 30):
                self.last_retrain_time = current_time
                RETRAIN_COUNT.inc()
                logger.warning(f"DRIFT THRESHOLD BREACHED (Score: {drift_res['drift_score']}). Triggering automated retraining pipeline!")
                model_service.retrain_model()

    def stop(self):
        self.running = False
        if self.consumer:
            self.consumer.close()

drift_consumer = EventConsumer()
