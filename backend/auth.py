"""
auth.py - Google OAuth2 login using requests-oauthlib.
Blueprint prefix: /auth
"""

from flask import Blueprint, redirect, request, session, current_app, jsonify
from requests_oauthlib import OAuth2Session
from database import db
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

GOOGLE_AUTH_URL   = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL  = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO   = "https://www.googleapis.com/oauth2/v2/userinfo"

# FIXED SCOPES
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]


def _make_session(state=None, token=None):
    cfg = current_app.config

    return OAuth2Session(
        client_id=cfg["GOOGLE_CLIENT_ID"],
        redirect_uri=cfg["GOOGLE_REDIRECT_URI"],
        scope=SCOPES,
        state=state,
        token=token,
    )


@auth_bp.route("/login")
def login():
    google = _make_session()

    authorization_url, state = google.authorization_url(
        GOOGLE_AUTH_URL,
        access_type="offline",
        prompt="select_account"
    )

    session["oauth_state"] = state
    return redirect(authorization_url)


@auth_bp.route("/callback")
def callback():
    cfg = current_app.config

    google = _make_session(state=session.get("oauth_state"))

    # FIX: safer token fetch
    token = google.fetch_token(
        GOOGLE_TOKEN_URL,
        client_secret=cfg["GOOGLE_CLIENT_SECRET"],
        authorization_response=request.url,
        include_client_id=True
    )

    session["oauth_token"] = token

    # Get user info
    user_info = google.get(GOOGLE_USERINFO).json()

    google_id = user_info.get("id")
    email     = user_info.get("email")
    name      = user_info.get("name")
    picture   = user_info.get("picture")

    if not google_id:
        return jsonify({"error": "Google login failed"}), 400

    # Create or update user
    user = User.query.filter_by(google_id=google_id).first()

    if not user:
        user = User(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture
        )
        db.session.add(user)
    else:
        user.name = name
        user.picture = picture

    db.session.commit()

    session["user_id"] = user.id

    return redirect("/chat.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@auth_bp.route("/me")
def me():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "not_authenticated"}), 401

    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "user_not_found"}), 404

    cfg = current_app.config

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
        "is_premium": user.is_premium,
        "today_count": user.today_count(),
        "daily_limit": cfg["FREE_DAILY_LIMIT"],
    })