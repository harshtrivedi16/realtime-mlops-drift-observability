from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from prometheus_client import make_asgi_app
import os
import time
import asyncio
from app.models.model import model_service
from app.kafka_producer import event_producer
from app.kafka_consumer import drift_consumer
from app.metrics import PREDICTION_COUNT, PREDICTION_LATENCY, RETRAIN_COUNT
from app.drift_engine import drift_engine

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MLStream Drift Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

DRIFT_SIMULATION_STATUS = {"active": False, "drift_enabled": False}

class PredictRequest(BaseModel):
    features: list[float]

class FeedbackRequest(BaseModel):
    prediction_id: str
    ground_truth: int

@app.on_event("startup")
def startup_event():
    drift_consumer.start()

@app.on_event("shutdown")
def shutdown_event():
    drift_consumer.stop()

@app.get("/")
def read_root():
    return {
        "status": "MLStream Gateway Online",
        "model_version": model_service.model_version,
        "kafka_broker": os.getenv("KAFKA_BROKER_URL", "localhost:9092"),
        "stream_simulator": DRIFT_SIMULATION_STATUS,
        "current_drift": drift_engine.calculate_drift()
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/predict")
def predict(request: PredictRequest):
    start_time = time.time()
    
    result = model_service.predict(request.features)
    result["timestamp"] = time.time()
    result["model_version"] = model_service.model_version

    event_producer.send_inference_log(result)
    
    if not event_producer.producer:
        drift_consumer.process_message(result)

    latency = time.time() - start_time
    PREDICTION_COUNT.labels(model_version=model_service.model_version).inc()
    PREDICTION_LATENCY.observe(latency)

    return result

@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    payload = {
        "prediction_id": request.prediction_id,
        "ground_truth": request.ground_truth,
        "timestamp": time.time()
    }
    event_producer.send_ground_truth(payload)
    return {"status": "feedback_received", "payload": payload}

@app.post("/retrain")
def trigger_manual_retrain():
    RETRAIN_COUNT.inc()
    record = model_service.retrain_model()
    return {"status": "retraining_triggered", "record": record}

@app.get("/retrain/history")
def get_retrain_history():
    return {"history": model_service.retraining_history}

async def stream_traffic_loop(drift: bool, delay_seconds: float):
    DRIFT_SIMULATION_STATUS["active"] = True
    DRIFT_SIMULATION_STATUS["drift_enabled"] = drift
    
    while DRIFT_SIMULATION_STATUS["active"]:
        samples = model_service.generate_synthetic_data(drift=DRIFT_SIMULATION_STATUS["drift_enabled"], count=1)
        sample = samples[0]
        sample["timestamp"] = time.time()
        sample["model_version"] = model_service.model_version
        
        event_producer.send_inference_log(sample)
        
        if not event_producer.producer:
            drift_consumer.process_message(sample)

        event_producer.send_ground_truth({
            "prediction_id": sample["prediction_id"],
            "ground_truth": sample["ground_truth"],
            "timestamp": time.time()
        })
        
        PREDICTION_COUNT.labels(model_version=model_service.model_version).inc()
        await asyncio.sleep(delay_seconds)

@app.post("/stream/start")
def start_stream_simulation(background_tasks: BackgroundTasks, drift: bool = False, delay_seconds: float = 0.5):
    if not DRIFT_SIMULATION_STATUS["active"]:
        background_tasks.add_task(stream_traffic_loop, drift, delay_seconds)
        return {"message": "Traffic stream simulator started", "drift": drift}
    else:
        DRIFT_SIMULATION_STATUS["drift_enabled"] = drift
        return {"message": "Traffic stream updated", "drift": drift}

@app.post("/stream/stop")
def stop_stream_simulation():
    DRIFT_SIMULATION_STATUS["active"] = False
    return {"message": "Traffic stream simulator stopped"}
