"""
app.py - Flask application factory.
Run:  flask run   or   python app.py
"""
import os
from flask import Flask, send_from_directory
from config import Config
from database import init_db
from auth import auth_bp
from chat import chat_bp
from integration import int_bp

# Allow HTTP for local dev (OAuth2Session default requires HTTPS)
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")


def create_app(config_class=Config):
    app = Flask(__name__, static_folder="../frontend", static_url_path="")
    app.config.from_object(config_class)

    # Database
    init_db(app)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(int_bp)

    # Serve frontend HTML directly
    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/<path:filename>")
    def static_files(filename):
        return send_from_directory(app.static_folder, filename)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, host="0.0.0.0", port=5000)