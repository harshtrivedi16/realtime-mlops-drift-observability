import numpy as np
import pytest
from app.drift_engine import DriftDetector

@pytest.fixture
def drift_detector():
    # Initialize with a small window size for fast testing
    return DriftDetector(window_size=20, features_count=5)

def test_no_drift_detected_on_baseline(drift_detector):
    """Test that feeding data from the exact baseline distribution does NOT trigger drift."""
    np.random.seed(100)
    # Generate 20 samples identical to baseline params (loc=0, scale=1)
    baseline_samples = np.random.normal(loc=0.0, scale=1.0, size=(20, 5))
    
    for sample in baseline_samples:
        drift_detector.add_sample(sample.tolist())
        
    result = drift_detector.calculate_drift()
    
    assert result["is_drifting"] is False
    assert result["drift_score"] < 0.15, f"Drift score too high for baseline data: {result['drift_score']}"
    assert len(result["details"]) == 5

def test_drift_detected_on_shifted_distribution(drift_detector):
    """Test that feeding heavily shifted data (concept drift) triggers the drift alarm."""
    np.random.seed(101)
    # Generate 20 samples from a shifted distribution (loc=3.0, scale=2.0)
    shifted_samples = np.random.normal(loc=3.0, scale=2.0, size=(20, 5))
    
    for sample in shifted_samples:
        drift_detector.add_sample(sample.tolist())
        
    result = drift_detector.calculate_drift()
    
    assert result["is_drifting"] is True
    assert result["drift_score"] >= 0.15, f"Drift score too low for shifted data: {result['drift_score']}"

def test_insufficient_data_returns_zero_drift():
    """Test that the engine returns 0 drift until the sliding window minimum is met."""
    detector = DriftDetector(window_size=100)
    
    # Add only 10 samples (requires at least window_size // 2 = 50)
    for _ in range(10):
        detector.add_sample([0.0, 0.0, 0.0, 0.0, 0.0])
        
    result = detector.calculate_drift()
    assert result["is_drifting"] is False
    assert result["drift_score"] == 0.0
