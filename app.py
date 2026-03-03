from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime

from database import users_collection, predictions_collection
import auth
import middleware
import github_fetcher
import feature_engineering
import model as ml_model
from sentiment import get_sentiment

load_dotenv()

app = Flask(__name__, static_folder="frontend/static", template_folder="frontend/templates")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
CORS(app)

# Ensure model is loaded at startup
ml_model.load_model()

# -------------------- Routes --------------------
@app.route("/")
def index():
    return send_from_directory(app.template_folder, "index.html")

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    user_id = auth.register_user(email, password)
    if not user_id:
        return jsonify({"error": "User already exists"}), 409
    token = auth.generate_token(user_id)
    return jsonify({"token": token}), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    user = auth.authenticate_user(email, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    token = auth.generate_token(user["_id"])
    return jsonify({"token": token}), 200

@app.route("/api/analyze", methods=["GET"])
@middleware.token_required
def analyze():
    github_username = request.args.get("github_username", "").strip()
    if not github_username:
        return jsonify({"error": "github_username parameter required"}), 400

    try:
        commits = github_fetcher.fetch_commits(github_username)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Feature engineering
    features = feature_engineering.compute_features(commits)

    # Prediction
    level, confidence, recommendation = ml_model.predict_burnout(features)

    # Store in database
    predictions_collection.insert_one({
        "user_id": request.user_id,
        "github_username": github_username,
        "extracted_features": features,
        "burnout_level": level,
        "confidence": confidence,
        "recommendation": recommendation,
        "timestamp": datetime.utcnow()
    })

    # Prepare data for frontend charts
    commit_dates = [c["date"][:10] for c in commits]
    commit_messages = [c["message"] for c in commits]
    sentiment_scores = [get_sentiment(msg) for msg in commit_messages]

    response = {
        "burnout_level": level,
        "confidence": confidence,
        "recommendation": recommendation,
        "features": features,
        "commit_dates": commit_dates,
        "sentiment_scores": sentiment_scores
    }
    return jsonify(response), 200

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    app.run(debug=True)