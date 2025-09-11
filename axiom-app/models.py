# In models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    fact_checks = db.relationship('FactCheck', backref='author', lazy=True)

class FactCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    claim_text = db.Column(db.Text, nullable=False)
    verdict = db.Column(db.String(50))
    # This is the key for anonymous users!
    # It links to a User, but can be empty (nullable=True).
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    sources = db.relationship('Source', backref='fact_check', lazy=True, cascade="all, delete-orphan")

class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    # This links each source back to its specific fact-check.
    fact_check_id = db.Column(db.Integer, db.ForeignKey('fact_check.id'), nullable=False)