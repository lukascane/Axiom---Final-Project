from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the database extension
db = SQLAlchemy()

# This is our User model, updated for Flask-Login
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    threads = db.relationship('ChatThread', backref='author', lazy=True, cascade="all, delete-orphan")

# This model represents a single conversation thread.
class ChatThread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # NEW: This flag controls the visibility of the thread.
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    messages = db.relationship('ChatMessage', backref='thread', lazy=True, cascade="all, delete-orphan", order_by='ChatMessage.timestamp')

# This model stores every individual message.
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('chat_thread.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        """Helper to convert message object to a dictionary."""
        return {
            "id": self.id,
            "role": self.role,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() + "Z"
        }

