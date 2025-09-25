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
    # This links a user to all the chat threads they have started.
    threads = db.relationship('ChatThread', backref='author', lazy=True, cascade="all, delete-orphan")

# This new model acts as a container for a single conversation.
class ChatThread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # This links a thread to all the messages inside it.
    messages = db.relationship('ChatMessage', backref='thread', lazy=True, cascade="all, delete-orphan", order_by='ChatMessage.timestamp')

# This new model stores every individual message from both the user and the AI.
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('chat_thread.id'), nullable=False)
    # The role will be either 'user' or 'assistant'.
    role = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        """A helper function to easily convert a message object into a dictionary."""
        return {
            "id": self.id,
            "role": self.role,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() + "Z"
        }

