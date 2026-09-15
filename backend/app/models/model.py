import numpy as np
from sklearn.ensemble import RandomForestClassifier
import uuid
import time

class MLModelService:
    def __init__(self):
        # 5 baseline features for classification
        self.feature_names = ["feature_1", "feature_2", "feature_3", "feature_4", "feature_5"]
        self.model = RandomForestClassifier(n_estimators=10, random_state=42)
        self.model_version = "v1.0.0"
        self.retraining_history = []
        self._train_baseline()

    def _train_baseline(self, loc=0.0, scale=1.0):
        # Train baseline model on standard distribution
        np.random.seed(42)
        X_train = np.random.normal(loc=loc, scale=scale, size=(1000, 5))
        y_train = (X_train[:, 0] + X_train[:, 1] * 0.5 > 0).astype(int)
        self.model.fit(X_train, y_train)

    def predict(self, features: list[float]):
        X = np.array(features).reshape(1, -1)
        prediction = int(self.model.predict(X)[0])
        probabilities = self.model.predict_proba(X)[0].tolist()
        prediction_id = str(uuid.uuid4())
        
        return {
            "prediction_id": prediction_id,
            "prediction": prediction,
            "probabilities": probabilities,
            "features": features
        }

    def retrain_model(self, new_loc=2.5, new_scale=1.5):
        """Simulates automated model retraining on new shifted data to eliminate drift."""
        # Increment version
        v_num = int(self.model_version.split(".")[-2]) + 1
        self.model_version = f"v1.{v_num}.0"
        
        # Re-train on new feature distribution
        self._train_baseline(loc=new_loc, scale=new_scale)
        
        record = {
            "version": self.model_version,
            "timestamp": time.time(),
            "status": "COMPLETED",
            "message": f"Automated retraining successful. Updated model to {self.model_version} on shifted distribution (mean={new_loc})."
        }
        self.retraining_history.append(record)
        return record

    def generate_synthetic_data(self, drift: bool = False, count: int = 1):
        loc = 2.5 if drift else 0.0
        scale = 1.5 if drift else 1.0
        
        data = []
        for _ in range(count):
            features = np.random.normal(loc=loc, scale=scale, size=5).tolist()
            res = self.predict(features)
            true_label = int(features[0] + features[1] * 0.5 > 0)
            res["ground_truth"] = true_label
            data.append(res)
        return data

model_service = MLModelService()
