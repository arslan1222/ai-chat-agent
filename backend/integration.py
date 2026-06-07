"""
integrations.py - WhatsApp & e-commerce settings.
Blueprint prefix: /api/integrations
"""
from flask import Blueprint, request, jsonify, session
from database import db
from models import User, Integration

int_bp = Blueprint("integrations", __name__, url_prefix="/api/integrations")


def _get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


@int_bp.route("/", methods=["GET"])
def get_settings():
    user = _get_current_user()
    if not user:
        return jsonify({"error": "not_authenticated"}), 401

    intg = user.integrations
    if not intg:
        return jsonify({})

    return jsonify({
        "whatsapp": {
            "number":  intg.wa_number,
            "api_key": "***" if intg.wa_api_key else None,
            "enabled": intg.wa_enabled,
        },
        "ecommerce": {
            "store_type": intg.ec_store_type,
            "store_url":  intg.ec_store_url,
            "api_key":    "***" if intg.ec_api_key else None,
            "enabled":    intg.ec_enabled,
        },
    })


@int_bp.route("/whatsapp", methods=["POST"])
def save_whatsapp():
    user = _get_current_user()
    if not user:
        return jsonify({"error": "not_authenticated"}), 401

    body = request.get_json(silent=True) or {}
    number  = body.get("number", "").strip()
    api_key = body.get("api_key", "").strip()
    enabled = bool(body.get("enabled", False))

    intg = user.integrations or Integration(user_id=user.id)
    intg.wa_number  = number  or intg.wa_number
    intg.wa_api_key = api_key or intg.wa_api_key
    intg.wa_enabled = enabled

    if not user.integrations:
        db.session.add(intg)
    db.session.commit()
    return jsonify({"ok": True, "enabled": intg.wa_enabled})


@int_bp.route("/ecommerce", methods=["POST"])
def save_ecommerce():
    user = _get_current_user()
    if not user:
        return jsonify({"error": "not_authenticated"}), 401

    body = request.get_json(silent=True) or {}
    store_type = body.get("store_type", "custom")
    store_url  = body.get("store_url", "").strip()
    api_key    = body.get("api_key", "").strip()
    enabled    = bool(body.get("enabled", False))

    intg = user.integrations or Integration(user_id=user.id)
    intg.ec_store_type = store_type
    intg.ec_store_url  = store_url  or intg.ec_store_url
    intg.ec_api_key    = api_key    or intg.ec_api_key
    intg.ec_enabled    = enabled

    if not user.integrations:
        db.session.add(intg)
    db.session.commit()
    return jsonify({"ok": True, "enabled": intg.ec_enabled})


# ── WhatsApp webhook receiver (example) ─────────────────────────────────────
@int_bp.route("/whatsapp/webhook", methods=["POST"])
def whatsapp_webhook():
    """
    Receive an inbound WhatsApp message via the Cloud API webhook,
    call the AI model, and send a reply back.
    Extend this with your actual WhatsApp provider SDK/calls.
    """
    data = request.get_json(silent=True) or {}
    # TODO: validate request signature, parse incoming message,
    #       look up associated user/integration, call chat._call_model(),
    #       then POST the reply to the WhatsApp Cloud API.
    return jsonify({"status": "received"}), 200