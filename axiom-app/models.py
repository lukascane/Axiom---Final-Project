# I need to import UserMixin, a helper class from Flask-Login.
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# I'm changing this class definition.
# By adding UserMixin, my User class will automatically get all the
# properties that Flask-Login needs, like is_active, is_authenticated, etc.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    fact_checks = db.relationship('FactCheck', backref='author', lazy=True)

# The rest of the models are correct and don't need any changes.
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

