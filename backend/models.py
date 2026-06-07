from database import db
from datetime import date

class User(db.Model):
    __tablename__ = "users"

    id         = db.Column(db.Integer, primary_key=True)
    google_id  = db.Column(db.String(128), unique=True, nullable=False)
    email      = db.Column(db.String(255), unique=True, nullable=False)
    name       = db.Column(db.String(255))
    picture    = db.Column(db.Text)
    is_premium = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    usages       = db.relationship("DailyUsage",  back_populates="user", cascade="all,delete")
    messages     = db.relationship("Conversation", back_populates="user", cascade="all,delete")
    integrations = db.relationship("Integration",  back_populates="user", cascade="all,delete", uselist=False)

    def today_count(self):
        row = DailyUsage.query.filter_by(user_id=self.id, usage_date=date.today()).first()
        return row.msg_count if row else 0

    def increment_usage(self):
        row = DailyUsage.query.filter_by(user_id=self.id, usage_date=date.today()).first()
        if row:
            row.msg_count += 1
        else:
            row = DailyUsage(user_id=self.id, usage_date=date.today(), msg_count=1)
            db.session.add(row)
        db.session.commit()


class DailyUsage(db.Model):
    __tablename__ = "daily_usage"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    usage_date = db.Column(db.Date, nullable=False)
    msg_count  = db.Column(db.Integer, default=0)

    user = db.relationship("User", back_populates="usages")


class Conversation(db.Model):
    __tablename__ = "conversations"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role       = db.Column(db.Enum("user", "assistant"), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", back_populates="messages")


class Integration(db.Model):
    __tablename__ = "integrations"

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    # WhatsApp
    wa_number     = db.Column(db.String(32))
    wa_api_key    = db.Column(db.Text)
    wa_enabled    = db.Column(db.Boolean, default=False)
    # E-commerce
    ec_store_type = db.Column(db.Enum("shopify", "woocommerce", "custom"), default="custom")
    ec_store_url  = db.Column(db.String(512))
    ec_api_key    = db.Column(db.Text)
    ec_enabled    = db.Column(db.Boolean, default=False)
    updated_at    = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    user = db.relationship("User", back_populates="integrations")