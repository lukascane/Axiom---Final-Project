from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# We initialize the db object here, but it will be configured in app.py
db = SQLAlchemy()

# We won't create a User model for now to keep it simple.
# We will assume a single user with id=1.

class Thread(db.Model):
    __tablename__ = 'threads'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default="New Conversation")
    # In a real app, this would be a foreign key to a User model.
    user_id = db.Column(db.Integer, nullable=False)
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # This relationship will automatically load all messages for a thread.
    # The 'cascade' option means deleting a thread will also delete all its messages.
    messages = db.relationship('Message', backref='thread', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        """Returns the object data in a dictionary format."""
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
    # The 'role' is important for the AI. It's either 'user' or 'assistant'.
    role = db.Column(db.String(50), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Returns the object data in a dictionary format."""
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "content": self.content,
            "role": self.role,
            "created_date": self.created_date.isoformat()
        }