# --- IMPORTS ---
# I need to add 'redirect' and 'url_for' to handle navigation between my new pages.
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
# I'm updating this to point to my new '/login' page route.
login_manager.login_view = 'login_page'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- NEW: HTML PAGE ROUTES ---

# The main entry point of my app will now be the public home page.
@app.route('/')
def index():
    return redirect(url_for('home_page'))

# This route serves the public home page.
@app.route('/home')
def home_page():
    return render_template('home.html')

# This route serves the user's private history page. It requires login.
@app.route('/history')
@login_required
def history_page():
    return render_template('history.html')

# This route handles starting a brand new chat.
@app.route('/chat')
@login_required
def new_chat_page():
    # It renders the chat template, but without a thread ID.
    # The JavaScript on the page will see this and start a new thread.
    return render_template('chat.html', thread_id=None, is_owner=True)

# This route handles viewing an existing chat, either public or private.
@app.route('/chat/<int:thread_id>')
def view_chat_thread(thread_id):
    thread = ChatThread.query.get_or_404(thread_id)
    
    # My security check: If the thread is private, only the owner can see it.
    if not thread.is_public and (not current_user.is_authenticated or current_user.id != thread.user_id):
        return "This chat is private and you are not authorized to view it.", 403
        
    # I'll tell the template if the current user is the owner.
    # This allows me to show/hide buttons like "delete" or the message input box.
    is_owner = current_user.is_authenticated and current_user.id == thread.user_id
    return render_template('chat.html', thread_id=thread.id, is_owner=is_owner)

# NEW: Routes to serve the login and signup pages.
@app.route('/login', methods=['GET'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('history_page'))
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def signup_page():
    if current_user.is_authenticated:
        return redirect(url_for('history_page'))
    return render_template('signup.html')


# --- AUTHENTICATION API ROUTES ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401
    login_user(user)
    # I'm adding a redirect_url to the response for a better user experience.
    return jsonify({"message": "Logged in successfully", "redirect_url": url_for('history_page')}), 200

@app.route('/signup', methods=['POST'])
def signup():
    # No changes needed here.
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


# --- CHATBOT & DATA API ROUTES ---

@app.route('/api/chat/start', methods=['POST'])
@login_required
def start_chat():
    # No changes needed here.
    new_thread = ChatThread(author=current_user)
    db.session.add(new_thread)
    db.session.commit()
    return jsonify({"message": "New chat thread created", "thread_id": new_thread.id}), 201

@app.route('/api/chat/<int:thread_id>/message', methods=['POST'])
@login_required
def send_message(thread_id):
    # No changes needed here.
    thread = ChatThread.query.get_or_404(thread_id)
    if thread.user_id != current_user.id:
        return jsonify({"error": "You are not authorized to post in this thread"}), 403

    user_message_count = ChatMessage.query.filter_by(thread_id=thread_id, role='user').count()
    if user_message_count >= 5:
        return jsonify({"error": "Conversation limit reached."}), 403

    data = request.get_json()
    user_message_text = data.get('message')

    if not user_message_text or len(user_message_text) > 1000:
        return jsonify({"error": "Message is missing or too long"}), 400

    user_message = ChatMessage(thread_id=thread.id, role='user', message=user_message_text)
    db.session.add(user_message)
    db.session.commit()

    history_messages = thread.messages
    messages_for_ai = [{"role": "system", "content": "You are a helpful and concise assistant."}]
    for msg in history_messages:
        messages_for_ai.append({"role": msg.role, "content": msg.message})

    ai_response_text = get_ai_chat_response(messages_for_ai)

    ai_message = ChatMessage(thread_id=thread.id, role='assistant', message=ai_response_text)
    db.session.add(ai_message)
    db.session.commit()

    return jsonify(ai_message.to_dict()), 200

# NEW: API endpoint to delete a thread, as per my diagram.
@app.route('/api/thread/<int:thread_id>', methods=['DELETE'])
@login_required
def delete_thread(thread_id):
    thread = ChatThread.query.get_or_404(thread_id)
    # My security check: I can only delete my own threads.
    if thread.user_id != current_user.id:
        return jsonify({"error": "You are not authorized to delete this thread"}), 403
    
    db.session.delete(thread)
    db.session.commit()
    return jsonify({"message": "Thread deleted successfully"})

# NEW: API endpoint to toggle public/private status.
@app.route('/api/thread/<int:thread_id>/toggle_public', methods=['POST'])
@login_required
def toggle_public(thread_id):
    thread = ChatThread.query.get_or_404(thread_id)
    if thread.user_id != current_user.id:
        return jsonify({"error": "You are not authorized to change this setting"}), 403
    
    thread.is_public = not thread.is_public
    db.session.commit()
    return jsonify({"message": "Visibility updated", "is_public": thread.is_public})

# NEW: API endpoint for my history page.
@app.route('/api/history', methods=['GET'])
@login_required
def get_user_history():
    threads = ChatThread.query.filter_by(user_id=current_user.id).order_by(ChatThread.created_at.desc()).all()
    history_data = []
    for t in threads:
        # I'll use the first user message as a title for the thread.
        first_user_message = next((msg for msg in t.messages if msg.role == 'user'), None)
        title = first_user_message.message[:50] + "..." if first_user_message and len(first_user_message.message) > 50 else (first_user_message.message if first_user_message else "New Chat")
        
        history_data.append({
            "id": t.id,
            "title": title,
            "created_at": t.created_at.strftime("%Y-%m-%d %H:%M"),
            "is_public": t.is_public
        })
    return jsonify(history_data)

# NEW: API endpoint for my public home page.
@app.route('/api/public_threads', methods=['GET'])
def get_public_threads():
    threads = ChatThread.query.filter_by(is_public=True).order_by(ChatThread.created_at.desc()).all()
    public_data = []
    for t in threads:
        first_user_message = next((msg for msg in t.messages if msg.role == 'user'), None)
        title = first_user_message.message[:50] + "..." if first_user_message and len(first_user_message.message) > 50 else (first_user_message.message if first_user_message else "Public Chat")
        
        public_data.append({
            "id": t.id,
            "title": title,
            "author_email": t.author.email,
            "created_at": t.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return jsonify(public_data)
    
# This retrieves the messages for a specific chat.
@app.route('/api/chat/<int:thread_id>', methods=['GET'])
def get_chat_history(thread_id):
    thread = ChatThread.query.get_or_404(thread_id)
    # My security check for private threads.
    if not thread.is_public and (not current_user.is_authenticated or current_user.id != thread.user_id):
        return jsonify({"error": "You are not authorized to access this thread"}), 403
    return jsonify([msg.to_dict() for msg in thread.messages]), 200

# --- RUN THE APP ---
if __name__ == '__main__':
    with app.app_context():
        db..create_all()
    app.run(debug=True, port=5000)
