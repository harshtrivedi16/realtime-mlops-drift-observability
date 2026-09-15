from prometheus_client import Counter, Histogram, Gauge

# Inference Telemetry
PREDICTION_COUNT = Counter("mlstream_predictions_total", "Total predictions served", ["model_version"])
PREDICTION_LATENCY = Histogram("mlstream_prediction_latency_seconds", "Latency of prediction requests")

# Drift Observability
DRIFT_SCORE = Gauge("mlstream_concept_drift_score", "Real-time composite drift score")
IS_DRIFTING = Gauge("mlstream_is_drifting", "Boolean flag (1=True, 0=False) indicating if drift is detected")

# Automated MLOps Action Telemetry
RETRAIN_COUNT = Counter("mlstream_retrain_events_total", "Total automated model retraining triggers executed")
