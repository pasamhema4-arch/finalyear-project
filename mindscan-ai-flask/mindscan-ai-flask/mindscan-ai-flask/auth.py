from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from models import db, User, bcrypt


# Initialize blueprint and bcrypt
auth_bp = Blueprint("auth", __name__)


# ======================
# REGISTER ENDPOINT
# ======================
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    # Validate input
    if not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"message": "All fields (username, email, password) are required"}), 400

    # Check if user already exists
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already registered"}), 400

    # Create user and hash password
    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])

    # Save to DB
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# ======================
# LOGIN ENDPOINT
# ======================
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    # Get user
    user = User.query.filter_by(email=email).first()

    # Verify password
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "access_token": access_token,
            "username": user.username,
            "language": user.language
        }), 200

    return jsonify({"message": "Invalid credentials"}), 401
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()

    user = db.session.get(User, user_id)  # ✅ safer for SQLAlchemy 2.x

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "language": user.language,
        "mental_health_score": user.mental_health_score,
        "privacy_settings": user.privacy_settings
    }), 200

# ======================
# UPDATE PROFILE & SETTINGS
# ======================
@auth_bp.route("/update-profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    if "privacy_settings" in data:
        user.privacy_settings = data["privacy_settings"]
    
    db.session.commit()
    return jsonify({"message": "Profile updated successfully"})

# ======================
# MOCK PASSWORD RESET
# ======================
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"message": "Password reset link sent to email (mocked)"})
    return jsonify({"message": "If the email is registered, a link has been sent."})

# ======================
# DELETE ACCOUNT
# ======================
@auth_bp.route("/delete-account", methods=["DELETE"])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
        
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Account securely deleted"})