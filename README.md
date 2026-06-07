# 🤖 AI Chat Agent

> AI-powered web chat with Google Login, GPT-OSS-120B, WhatsApp & E-commerce integration — built with Python (Flask), JavaScript, and MySQL.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES2023-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## What It Does

Users log in via Google, chat with a GPT-OSS-120B model (via [Cerebras.ai](https://cerebras.ai) or [GroqCloud](https://groq.com)), and get **100 free messages/day**. Admins can connect the agent to **WhatsApp Business** and **e-commerce stores** (Shopify, WooCommerce) for automated customer support. All conversations are saved in MySQL.

---

## Features

| | |
|---|---|
| 🔐 Google OAuth2 Login | Secure sign-in, no passwords |
| 💬 GPT-OSS-120B Chat | Real-time AI responses |
| 📊 Daily Usage Counter | 100 msg free tier per user/day |
| 📱 WhatsApp Integration | Store number + API key, webhook-ready |
| 🛒 E-commerce Integration | Shopify / WooCommerce / custom |
| 🗃️ Conversation History | Full history stored in MySQL |
| ⭐ Premium Upgrade Page | Free / Pro / Enterprise tiers |

---

## Project Structure

```
ai-chat-agent/
├── backend/
│   ├── app.py              # Flask factory & routes
│   ├── config.py           # Settings via .env
│   ├── database.py         # SQLAlchemy init
│   ├── models.py           # User, Conversation, Integration, DailyUsage
│   ├── auth.py             # Google OAuth2  →  /auth/*
│   ├── chat.py             # AI chat API    →  /api/chat/*
│   ├── integrations.py     # WA + e-com     →  /api/integrations/*
│   ├── schema.sql          # MySQL DDL
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html          # Login page
    ├── chat.html           # Chat UI
    ├── settings.html       # Integration settings
    ├── premium.html        # Upgrade page
    ├── style.css
    ├── main.js             # Chat logic
    └── settings.js         # Settings logic
```

---

## Quick Start

### 1 — Clone & install

```bash
git clone https://github.com/your-username/ai-chat-agent.git
cd ai-chat-agent/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2 — Configure environment

```bash
cp .env.example .env
# Edit .env with your values:
```

```env
SECRET_KEY=your-flask-secret

DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=ai_chat_agent

GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback

AI_API_BASE_URL=https://api.cerebras.ai/v1
AI_API_KEY=your_api_key
AI_MODEL=llama3.1-70b

FREE_DAILY_LIMIT=100
```

> **Google Setup:** Go to [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials → Create OAuth 2.0 Client → add `http://localhost:5000/auth/callback` as redirect URI.

### 3 — Database

```bash
# Auto (SQLAlchemy creates tables on first run):
python app.py

# Or manual SQL:
mysql -u root -p < schema.sql
```

### 4 — Run

```bash
python app.py
# Open http://localhost:5000
```

---

## API Endpoints

### Auth
| Method | Route | Description |
|---|---|---|
| GET | `/auth/login` | Redirect to Google |
| GET | `/auth/callback` | OAuth callback |
| GET | `/auth/logout` | Clear session |
| GET | `/auth/me` | Current user + usage stats |

### Chat
| Method | Route | Description |
|---|---|---|
| POST | `/api/chat/send` | Send message → AI reply |
| GET | `/api/chat/history` | Full conversation history |
| DELETE | `/api/chat/clear` | Clear all messages |

**Send example:**
```json
POST /api/chat/send
{ "message": "Hello!" }

→ { "reply": "Hi! How can I help?", "count": 1, "limit": 100 }
```

**Limit reached (HTTP 429):**
```json
{ "error": "limit_reached", "count": 100, "limit": 100 }
```

### Integrations
| Method | Route | Description |
|---|---|---|
| GET | `/api/integrations/` | Load saved settings |
| POST | `/api/integrations/whatsapp` | Save WhatsApp config |
| POST | `/api/integrations/ecommerce` | Save e-commerce config |
| POST | `/api/integrations/whatsapp/webhook` | Receive inbound WA messages |

---

## Database Schema

```
users           → id, google_id, email, name, picture, is_premium
daily_usage     → user_id, usage_date, msg_count
conversations   → user_id, role (user/assistant), content, created_at
integrations    → user_id, wa_number, wa_api_key, ec_store_type, ec_store_url, ec_api_key
```

---

## Free Tier vs Premium

| | Free | Pro ($9/mo) | Enterprise |
|---|---|---|---|
| Messages/day | 100 | Unlimited | Unlimited |
| WhatsApp | Read-only | Full | Full |
| E-commerce stores | 1 | 5 | Unlimited |
| API access | — | ✅ | ✅ |

The `is_premium` flag on the `User` model bypasses all daily limit checks.

---

## Deployment

```bash
# Production with Gunicorn + Nginx
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

- Use **Nginx** as a reverse proxy in front of Gunicorn
- Get HTTPS via **Let's Encrypt / Certbot**
- Update `GOOGLE_REDIRECT_URI` to your live domain
- Remove `OAUTHLIB_INSECURE_TRANSPORT=1` in production

---

## Tech Stack

- **Backend:** Python 3.11, Flask 3, Flask-SQLAlchemy, PyMySQL, requests-oauthlib
- **Frontend:** Vanilla HTML / CSS / JavaScript (no framework needed)
- **Database:** MySQL 8.0
- **AI API:** Cerebras.ai or GroqCloud (OpenAI-compatible endpoints)
- **Auth:** Google OAuth2 via Google Cloud Console

