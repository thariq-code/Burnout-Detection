import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from database import users_collection

def register_user(email, password):
    if users_collection.find_one({"email": email}):
        return None
    hashed = generate_password_hash(password)
    user_id = users_collection.insert_one({
        "email": email,
        "password": hashed,
        "created_at": datetime.datetime.utcnow()
    }).inserted_id
    return str(user_id)

def authenticate_user(email, password):
    user = users_collection.find_one({"email": email})
    if user and check_password_hash(user["password"], password):
        return user
    return None

def generate_token(user_id):
    payload = {
        "user_id": str(user_id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")

def decode_token(token):
    try:
        payload = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
        return payload["user_id"]
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None