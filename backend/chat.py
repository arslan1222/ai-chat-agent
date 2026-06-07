"""
chat.py - Chat API endpoints.
Blueprint prefix: /api/chat
"""
import requests
from flask import (Blueprint, request, jsonify, session, current_app)
from database import db
from models import User, Conversation

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")

SYSTEM_PROMPT = (
    "You are a helpful AI assistant. "
    "Answer clearly and concisely. "
    "If you are assisting a customer on behalf of a business, "
    "be polite and professional."
)


def _get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def _call_model(messages: list[dict]) -> str:
    """
    Call the GPT-OSS-120B model through the configured API
    (Cerebras.ai or GroqCloud – both follow OpenAI-compatible format).
    """
    cfg = current_app.config
    payload = {
        "model": cfg["AI_MODEL"],
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7,
    }
    headers = {
        "Authorization": f"Bearer {cfg['AI_API_KEY']}",
        "Content-Type": "application/json",
    }
    resp = requests.post(
        f"{cfg['AI_API_BASE_URL']}/chat/completions",
        json=payload,
        headers=headers,
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


@chat_bp.route("/send", methods=["POST"])
def send():
    user = _get_current_user()
    if not user:
        return jsonify({"error": "not_authenticated"}), 401

    cfg = current_app.config
    today_count = user.today_count()

    # Enforce free-tier limit for non-premium users
    if not user.is_premium and today_count >= cfg["FREE_DAILY_LIMIT"]:
        return jsonify({
            "error": "limit_reached",
            "count": today_count,
            "limit": cfg["FREE_DAILY_LIMIT"],
        }), 429

    body = request.get_json(silent=True) or {}
    user_message = (body.get("message") or "").strip()
    if not user_message:
        return jsonify({"error": "empty_message"}), 400

    # Persist user message
    db.session.add(Conversation(user_id=user.id, role="user", content=user_message))
    db.session.commit()

    # Build message history for the model (last 20 turns for context)
    history = (
        Conversation.query
        .filter_by(user_id=user.id)
        .order_by(Conversation.created_at.asc())
        .limit(40)
        .all()
    )
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": h.role, "content": h.content} for h in history]

    try:
        assistant_reply = _call_model(messages)
    except Exception as exc:
        return jsonify({"error": "model_error", "detail": str(exc)}), 502

    # Persist assistant reply & increment usage
    db.session.add(Conversation(user_id=user.id, role="assistant", content=assistant_reply))
    db.session.commit()
    user.increment_usage()

    new_count = user.today_count()
    return jsonify({
        "reply":      assistant_reply,
        "count":      new_count,
        "limit":      cfg["FREE_DAILY_LIMIT"],
        "is_premium": user.is_premium,
    })


@chat_bp.route("/history", methods=["GET"])
def history():
    user = _get_current_user()
    if not user:
        return jsonify({"error": "not_authenticated"}), 401

    rows = (
        Conversation.query
        .filter_by(user_id=user.id)
        .order_by(Conversation.created_at.asc())
        .all()
    )
    return jsonify([
        {"role": r.role, "content": r.content, "ts": r.created_at.isoformat()}
        for r in rows
    ])


@chat_bp.route("/clear", methods=["DELETE"])
def clear():
    user = _get_current_user()
    if not user:
        return jsonify({"error": "not_authenticated"}), 401
    Conversation.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    return jsonify({"ok": True})