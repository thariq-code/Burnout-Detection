import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os

# Create synthetic training data (replace with real collected data in production)
np.random.seed(42)
n_samples = 2000

data = {
    "weekly_commit_frequency": np.random.uniform(0, 60, n_samples),
    "night_coding_ratio": np.random.uniform(0, 1, n_samples),
    "weekend_coding_ratio": np.random.uniform(0, 1, n_samples),
    "bug_fix_keyword_frequency": np.random.uniform(0, 1, n_samples),
    "average_sentiment": np.random.uniform(-1, 1, n_samples),
    "activity_consistency": np.random.uniform(0, 2, n_samples),
    "stress_pattern_indicator": np.random.uniform(0, 1, n_samples),
    "commit_count": np.random.randint(0, 300, n_samples)
}
df = pd.DataFrame(data)

# Generate target: 0=Low, 1=Medium, 2=High based on heuristic rules
conditions = [
    (df["weekly_commit_frequency"] < 15) & (df["night_coding_ratio"] < 0.3) & (df["average_sentiment"] > 0.2),
    (df["weekly_commit_frequency"] >= 15) & (df["weekly_commit_frequency"] < 35) | (df["night_coding_ratio"] > 0.5),
    (df["weekly_commit_frequency"] >= 35) | (df["night_coding_ratio"] > 0.8) | (df["stress_pattern_indicator"] > 0.7)
]
choices = [0, 1, 2]
df["burnout"] = np.select(conditions, choices, default=1)

X = df.drop("burnout", axis=1)
y = df["burnout"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/model.pkl")
print(f"Model saved to models/model.pkl. Accuracy: {model.score(X_test, y_test):.2f}")