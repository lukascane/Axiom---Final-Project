from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Thread(db.Model):
    __tablename__ = 'threads'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default="New Conversation")
    user_id = db.Column(db.Integer, nullable=False) # We will keep this simple for now
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='thread', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "user_id": self.user_id,
            "is_public": self.is_public,
            "created_date": self.created_date.isoformat()
        }

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('threads.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False) # 'user' or 'assistant'
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "content": self.content,
            "role": self.role,
            "created_date": self.created_date.isoformat()
        }

