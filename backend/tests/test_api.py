import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.model import model_service

client = TestClient(app)

def test_health_check():
    """Verify that the FastAPI gateway is healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_endpoint():
    """Verify that the /predict endpoint accepts a feature vector and returns a prediction ID."""
    payload = {
        "features": [0.5, -1.2, 3.4, 0.0, 1.1]
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "prediction_id" in data
    assert "prediction" in data
    assert "probabilities" in data
    assert "model_version" in data
    assert data["features"] == payload["features"]

def test_feedback_endpoint():
    """Verify that the /feedback endpoint accepts ground truth labels."""
    payload = {
        "prediction_id": "test-uuid-1234",
        "ground_truth": 1
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "feedback_received"

def test_manual_retrain_endpoint():
    """Verify that the /retrain endpoint increments the model version."""
    initial_version = model_service.model_version
    
    response = client.post("/retrain")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "retraining_triggered"
    assert data["record"]["version"] != initial_version
    
    # Verify history is stored
    history_resp = client.get("/retrain/history")
    assert history_resp.status_code == 200
    history_data = history_resp.json()["history"]
    assert len(history_data) > 0
    assert history_data[-1]["version"] == data["record"]["version"]
