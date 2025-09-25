# --- IMPORTS ---
# I'm adding Flask's 'render_template' to show my HTML page.
# I also need 'datetime' to work with timestamps.
from flask import Flask, request, jsonify, render_template
from datetime import datetime

# I'm replacing my old models with the new Chat-focused ones.
from models import db, User, ChatThread, ChatMessage
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# I'm importing my new, real AI engine.
# CHANGE NEEDED: This is the most important part to change later.
# Right now, it points to my placeholder engine.py file.
# To make the chatbot real, I will update engine.py to call the actual
# OpenAI API, but I won't need to change anything here in app.py.
from engine import get_ai_chat_response

# --- APP SETUP & CONFIGURATION ---
app = Flask(__name__)
# WHAT IT MEANS: The SECRET_KEY is critical for security. It's used by Flask
# to sign session cookies, which prevents users from tampering with them.
app.config['SECRET_KEY'] = 'a-super-secret-key-that-no-one-will-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///axiom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- USER AUTHENTICATION SETUP (No changes here) ---
login_manager = LoginManager()
login_manager.init_app(app)
# WHAT IT MEANS: If a user who is NOT logged in tries to access a page
# protected with @login_required, Flask will automatically redirect them
# to the page for the 'login' function.
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # WHAT IT MEANS: This function is how Flask-Login finds a user. After a user logs in,
    # their user_id is stored in the session cookie. On subsequent requests, Flask-Login
    # uses this function to load the full user object from the database using that ID.
    return User.query.get(int(user_id))

# --- HOMEPAGE ROUTE (No changes here) ---
@app.route('/')
def home():
    return render_template('index.html')

# --- AUTHENTICATION API ROUTES (No changes here) ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email address already registered"}), 409
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully!"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401
    login_user(user)
    return jsonify({"message": "Logged in successfully", "user_id": user.id}), 200

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200


# --- NEW CHATBOT API ROUTES ---

# This endpoint starts a new conversation.
@app.route('/api/chat/start', methods=['POST'])
@login_required
def start_chat():
    # I create a new thread and link it to the currently logged-in user.
    new_thread = ChatThread(author=current_user)
    db.session.add(new_thread)
    db.session.commit()
    return jsonify({"message": "New chat thread created", "thread_id": new_thread.id}), 201

# This endpoint handles sending a message within a specific conversation thread.
@app.route('/api/chat/<int:thread_id>/message', methods=['POST'])
@login_required
def send_message(thread_id):
    # First, I find the conversation thread.
    thread = ChatThread.query.get_or_404(thread_id)

    # WHAT IT MEANS: This is a critical security check. It ensures that a user
    # can only add messages to their OWN conversation threads, not someone else's.
    if thread.user_id != current_user.id:
        return jsonify({"error": "You are not authorized to access this thread"}), 403

    # TOKEN STRATEGY 1: Limit the number of messages per thread.
    # WHAT IT MEANS: This is my primary strategy for controlling costs. By limiting
    # each conversation to 5 user questions, I create a predictable maximum token
    # count for any single thread, preventing runaway expenses.
    user_message_count = ChatMessage.query.filter_by(thread_id=thread_id, role='user').count()
    if user_message_count >= 5:
        return jsonify({"error": "Conversation limit reached. Please start a new thread."}), 403

    data = request.get_json()
    user_message_text = data.get('message')

    # TOKEN STRATEGY 2: Limit the length of the user's message.
    # WHAT IT MEANS: This is a simple but effective safeguard. It prevents a user
    # from pasting a huge amount of text, which would use up a lot of tokens and
    # potentially exceed the AI model's context limit.
    if not user_message_text or len(user_message_text) > 1000:
        return jsonify({"error": "Message is missing or too long (max 1000 chars)"}), 400

    # I save the user's new message to the database.
    user_message = ChatMessage(thread_id=thread.id, role='user', message=user_message_text)
    db.session.add(user_message)
    db.session.commit()

    # Now, I prepare the entire conversation history for the AI.
    history_messages = thread.messages
    
    # This is the standard format OpenAI expects: a list of dictionaries.
    messages_for_ai = [
        {"role": "system", "content": "You are a helpful and concise assistant."}
    ]
    for msg in history_messages:
        messages_for_ai.append({"role": msg.role, "content": msg.message})

    # I call my new AI engine with the full history.
    # CHANGE NEEDED: This function call is what connects to my engine.py.
    # All the logic for actually calling the OpenAI API will live inside
    # the get_ai_chat_response function, keeping this file clean.
    ai_response_text = get_ai_chat_response(messages_for_ai)

    # I save the AI's response to the database.
    ai_message = ChatMessage(thread_id=thread.id, role='assistant', message=ai_response_text)
    db.session.add(ai_message)
    db.session.commit()

    # Finally, I send the AI's response back to the user.
    return jsonify(ai_message.to_dict()), 200

# This endpoint retrieves the full history of a single conversation.
@app.route('/api/chat/<int:thread_id>', methods=['GET'])
@login_required
def get_chat_history(thread_id):
    thread = ChatThread.query.get_or_404(thread_id)

    # WHAT IT MEANS: This is another security check to ensure a user can only
    # view the history of their own conversations.
    if thread.user_id != current_user.id:
        return jsonify({"error": "You are not authorized to access this thread"}), 403

    # I convert each message object into a dictionary and return the list.
    return jsonify([msg.to_dict() for msg in thread.messages]), 200


# --- RUN THE APP ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
