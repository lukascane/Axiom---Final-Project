# --- IMPORTS ---
from flask import Flask, request, jsonify, render_template, redirect, url_for
from models import db, User, ChatThread, ChatMessage
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from engine import get_ai_chat_response

# --- APP SETUP & CONFIGURATION ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-super-secret-key-that-no-one-will-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///axiom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- USER AUTHENTICATION SETUP ---
login_manager = LoginManager()
login_manager.init_app(app)
# FIX: Point login_view to the new page route, not the API endpoint.
login_manager.login_view = 'login_page'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- HTML PAGE ROUTES (NEW) ---
# These routes are responsible for showing the HTML pages to the user.

@app.route('/')
def index():
    # If the user is already logged in, take them to the chat. Otherwise, to login.
    if current_user.is_authenticated:
        return redirect(url_for('chat_page'))
    return redirect(url_for('login_page'))

@app.route('/chat')
@login_required
def chat_page():
    return render_template('chat.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')


# --- AUTHENTICATION API ROUTES ---
# These routes handle the form submissions from the JavaScript in your HTML files.

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401
    login_user(user)
    return jsonify({"message": "Logged in successfully"}), 200

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


# --- CHATBOT API ROUTES (No changes needed here) ---

@app.route('/api/chat/start', methods=['POST'])
@login_required
def start_chat():
    new_thread = ChatThread(author=current_user)
    db.session.add(new_thread)
    db.session.commit()
    return jsonify({"message": "New chat thread created", "thread_id": new_thread.id}), 201

@app.route('/api/chat/<int:thread_id>/message', methods=['POST'])
@login_required
def send_message(thread_id):
    thread = ChatThread.query.get_or_404(thread_id)
    if thread.user_id != current_user.id:
        return jsonify({"error": "You are not authorized to access this thread"}), 403

    user_message_count = ChatMessage.query.filter_by(thread_id=thread_id, role='user').count()
    if user_message_count >= 5:
        return jsonify({"error": "Conversation limit reached. Please start a new thread."}), 403

    data = request.get_json()
    user_message_text = data.get('message')

    if not user_message_text or len(user_message_text) > 1000:
        return jsonify({"error": "Message is missing or too long (max 1000 chars)"}), 400

    user_message = ChatMessage(thread_id=thread.id, role='user', message=user_message_text)
    db.session.add(user_message)
    db.session.commit()

    history_messages = thread.messages
    messages_for_ai = [
        {"role": "system", "content": "You are a helpful and concise assistant."}
    ]
    for msg in history_messages:
        messages_for_ai.append({"role": msg.role, "content": msg.message})

    ai_response_text = get_ai_chat_response(messages_for_ai)

    ai_message = ChatMessage(thread_id=thread.id, role='assistant', message=ai_response_text)
    db.session.add(ai_message)
    db.session.commit()

    return jsonify(ai_message.to_dict()), 200

@app.route('/api/chat/<int:thread_id>', methods=['GET'])
@login_required
def get_chat_history(thread_id):
    thread = ChatThread.query.get_or_404(thread_id)
    if thread.user_id != current_user.id:
        return jsonify({"error": "You are not authorized to access this thread"}), 403
    return jsonify([msg.to_dict() for msg in thread.messages]), 200

# --- RUN THE APP ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)