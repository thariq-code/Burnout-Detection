import joblib
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import tensorflow as tf
# use tf.keras to avoid import resolution issues
# from tensorflow import keras -> referenced as tf.keras throughout

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "model.pkl")
_model = None

def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_burnout(features_dict):
    """
    features_dict: dict with keys matching training features
    Returns (level, confidence, recommendation)
    """
    model = load_model()
    # Ensure feature order matches training
    feature_names = ["weekly_commit_frequency", "night_coding_ratio",
                     "weekend_coding_ratio", "bug_fix_keyword_frequency",
                     "average_sentiment", "activity_consistency",
                     "stress_pattern_indicator", "commit_count"]
    X = np.array([[features_dict[name] for name in feature_names]])
    
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    confidence = float(np.max(proba))
    
    levels = ["Low", "Medium", "High"]
    level = levels[int(pred)]
    
    # Recommendation based on level
    if level == "Low":
        rec = "Your coding patterns are healthy. Maintain work-life balance and keep up the good work!"
    elif level == "Medium":
        rec = "Some signs of stress detected. Consider regular breaks, exercise, and reviewing your workload."
    else:
        rec = "High burnout risk detected. It's strongly recommended to take time off, seek support, and reassign tasks."
    
    return level, confidence, rec

# Structure for XGBoost and LSTM (can be used if models are trained separately)
class XGBoostModel:
    def __init__(self, model_path):
        self.model = xgb.Booster()
        self.model.load_model(model_path)

    def predict(self, X):
        dmatrix = xgb.DMatrix(X)
        return self.model.predict(dmatrix)

class LSTMModel:
    def __init__(self, model_path):
        # use tf.keras to avoid extra import
        self.model = tf.keras.models.load_model(model_path)

    def predict(self, X):
        # Assuming X is 2D, LSTM expects 3D (samples, timesteps, features)
        # For simplicity, we reshape to (1, 1, n_features) – adjust as needed
        X = X.reshape((X.shape[0], 1, X.shape[1]))
        return self.model.predict(X)