import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt  # <-- 1. IMPORTED BCRYPT

# Initialize extensions, but they will be configured in app.py
db = SQLAlchemy()
bcrypt = Bcrypt()  # <-- 2. INITIALIZED BCRYPT

class User(db.Model, UserMixin):
    __tablename__ = 'user'  # <-- 3. RENAMED TABLE
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False) # <-- 4. CHANGED 'email' to 'username'
    password = db.Column(db.String(150), nullable=False) # <-- 5. RENAMED 'password_hash'
    
    threads = db.relationship('ChatThread', backref='user', lazy=True)

    # --- 6. ADDED HELPER METHODS ---
    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks if a provided password matches the hash."""
        return bcrypt.check_password_hash(self.password, password)

class ChatThread(db.Model):
    __tablename__ = 'chat_thread' # <-- 3. RENAMED TABLE
    
    # --- 7. CHANGED ID TO UUID ---
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    messages = db.relationship('ChatMessage', backref='thread', lazy=True, order_by='ChatMessage.created_at')

class ChatMessage(db.Model):
    __tablename__ = 'chat_message' # <-- 3. RENAMED TABLE
    id = db.Column(db.Integer, primary_key=True)
    
    # --- 7. UPDATED FOREIGN KEY TO UUID ---
    thread_id = db.Column(db.String(36), db.ForeignKey('chat_thread.id'), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False) # <-- 8. RENAMED 'message' to 'content'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)