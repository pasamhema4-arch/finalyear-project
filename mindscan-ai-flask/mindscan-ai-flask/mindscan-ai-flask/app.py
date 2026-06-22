from flask import Flask, render_template
from config import Config
from models import db
from auth import auth_bp
from analysis import analysis_bp
from flask_jwt_extended import JWTManager
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

app.config["JWT_SECRET_KEY"] = "super-secret-key"

db.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(analysis_bp, url_prefix="/analysis")

@app.route("/")
def root():
    return render_template("login.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/report")
def report():
    return render_template("report.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/journal")
def journal():
    return render_template("journal.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/games")
def games():
    return render_template("games.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)