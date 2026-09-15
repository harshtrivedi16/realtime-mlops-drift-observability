import numpy as np
from scipy.stats import ks_2samp, wasserstein_distance
from collections import deque
import logging

logger = logging.getLogger("mlstream-drift")

class DriftDetector:
    def __init__(self, window_size=100, features_count=5):
        self.window_size = window_size
        self.features_count = features_count
        self.sliding_window = deque(maxlen=window_size)
        
        # Baseline distribution (simulating the distribution the model was trained on)
        np.random.seed(42)
        self.baseline = np.random.normal(loc=0.0, scale=1.0, size=(1000, features_count))

    def add_sample(self, features: list[float]):
        if len(features) == self.features_count:
            self.sliding_window.append(features)

    def calculate_drift(self) -> dict:
        """
        Calculates drift across all features using KS-Test and Wasserstein distance.
        Returns a dictionary with drift metrics and a composite drift score.
        """
        if len(self.sliding_window) < self.window_size // 2:
            # Not enough data to confidently calculate drift
            return {"drift_score": 0.0, "is_drifting": False, "details": {}}

        current_data = np.array(self.sliding_window)
        total_drift_score = 0.0
        feature_details = {}
        is_drifting = False

        for i in range(self.features_count):
            base_f = self.baseline[:, i]
            curr_f = current_data[:, i]

            # 1. Kolmogorov-Smirnov Test
            ks_stat, p_value = ks_2samp(base_f, curr_f)
            
            # 2. Wasserstein Distance (Earth Mover's Distance)
            w_dist = wasserstein_distance(base_f, curr_f)

            # Composite feature drift score (normalized approximation)
            # KS stat is between 0 and 1. W-dist depends on scale, but we know base scale is ~1.0.
            f_drift = (ks_stat * 0.7) + (min(w_dist, 3.0) / 3.0 * 0.3)
            total_drift_score += f_drift

            feature_details[f"feature_{i+1}"] = {
                "ks_stat": round(ks_stat, 4),
                "p_value": round(p_value, 4),
                "wasserstein_dist": round(w_dist, 4),
                "drift_score": round(f_drift, 4)
            }

            # If p-value < 0.05, distributions are significantly different
            if p_value < 0.05 and f_drift > 0.15:
                is_drifting = True

        avg_drift_score = total_drift_score / self.features_count

        # Global drift threshold
        if avg_drift_score > 0.15:
            is_drifting = True

        return {
            "drift_score": round(avg_drift_score, 4),
            "is_drifting": is_drifting,
            "details": feature_details
        }

drift_engine = DriftDetector(window_size=50)
