import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

# --- 1. INITIALIZATION & CONFIGURATION ---
load_dotenv()

# Tell Flask where to find the 'templates' folder.
# '../frontend/templates' means "go up one directory from 'backend', then into 'frontend/templates'"
app = Flask(__name__, template_folder='../frontend/templates')
app.config['SECRET_KEY'] = 'a_very_secret_key_that_should_be_changed'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

# --- 2. IMPORT MODELS & SERVICES ---
# Import models and services *before* initializing extensions
# This brings in the uninitialized 'db' and 'bcrypt' from models.py
from models import db, bcrypt, User, ChatThread, ChatMessage
from ai_service import get_ai_response

# --- 3. INITIALIZE EXTENSIONS ---
# Now, initialize the imported instances with our app
# This is the correct pattern to avoid circular imports and errors.
db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    # Use the new, recommended db.session.get()
    return db.session.get(User, int(user_id))

# --- 4. HELPER COMMAND TO CREATE DB ---

@app.cli.command('create-db')
def create_db():
    """Creates the database and a default test user."""
    # We need to be in an app context to run DB operations
    with app.app_context():
        db.create_all()
    
        if not User.query.filter_by(username='testuser').first():
            print("Creating default user 'testuser' with password 'password'")
            test_user = User(username='testuser')
            test_user.set_password('password')
            db.session.add(test_user)
            db.session.commit()
            print("User 'testuser' created with id=1.")
        else:
            print("User 'testuser' already exists.")
        print("Database created!")

# --- 5. CORE CHAT API ENDPOINTS ---

@app.route('/api/chat/start', methods=['POST'])
# @login_required # <-- DISABLED FOR STEP 1 TESTING
def start_chat():
    """ Starts a new chat thread. """
    
    # --- TEMPORARY FIX FOR STEP 1 ---
    # We hardcode the user to '1' since we disabled login
    user_id = 1 
    # --- END TEMPORARY FIX ---

    # Use the new, recommended db.session.get()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Test user with id=1 not found. Run 'flask create-db' first."}), 404

    try:
        # Create a new thread with a UUID
        print(user_id)
        new_thread = ChatThread(user_id=user.id)
        db.session.add(new_thread)
        print(new_thread)
        
        # Add the initial welcome message from the assistant
        starter_message = ChatMessage(
            thread_id=new_thread.id,
            role="assistant",
            content="Hello! How can I help you today?"
        )
        db.session.add(starter_message)
        db.session.commit()
        
        print(f"New chat thread created: {new_thread.id}")
        return jsonify({
            "thread_id": new_thread.id,
            "message": "New chat thread created.",
            "created_at": new_thread.created_at.isoformat(),
            "first_message": "New Chat" # Default title
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error creating new chat: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/<string:thread_id>/message', methods=['POST'])
# @login_required # <-- DISABLED FOR STEP 1 TESTING
def post_message(thread_id):
    """ Posts a new user message to a thread and gets an AI response. """
    
    data = request.json
    user_message_content = data.get('message')

    if not user_message_content:
        return jsonify({"error": "No message content provided"}), 400

    # Use the new, recommended db.session.get()
    thread = db.session.get(ChatThread, thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), 404
        
    try:
        # 1. Add User's message to DB
        user_message = ChatMessage(
            thread_id=thread.id,
            role="user",
            content=user_message_content
        )
        db.session.add(user_message)
        db.session.commit() # Commit the user's message first

        # 2. Prepare context for AI (fetch all messages for this thread)
        messages_history = thread.messages
        
        # 3. Call AI Service (from ai_service.py)
        ai_response_content = get_ai_response(messages_history)

        # 4. Add AI's response to DB
        ai_message = ChatMessage(
            thread_id=thread.id,
            role="assistant",
            content=ai_response_content
        )
        db.session.add(ai_message)
        db.session.commit() # Commit the AI's message

        # 5. Return AI's response to the frontend
        return jsonify({"role": "assistant", "content": ai_response_content})

    except Exception as e:
        db.session.rollback()
        print(f"Error processing message: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/<string:thread_id>', methods=['GET'])
# @login_required # <-- DISABLED FOR STEP 1 TESTING
def get_chat_messages(thread_id):
    """ Gets all messages for a specific chat thread. """
    
    # Use the new, recommended db.session.get()
    thread = db.session.get(ChatThread, thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), 404

    messages = thread.messages # Already ordered by created_at (see models.py)
    
    messages_data = [
        {
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        } for msg in messages
    ]
    
    return jsonify(messages_data)

# --- 6. CHAT HISTORY & MANAGEMENT API (From Graph) ---

@app.route('/api/history', methods=['GET'])
# @login_required # <-- DISABLED FOR STEP 1 TESTING
def get_user_history():
    """ Gets all chat threads for the hardcoded test user. """
    
    # --- TEMPORARY FIX FOR STEP 1 ---
    user_id = 1
    # --- END TEMPORARY FIX ---
    
    threads = ChatThread.query.filter_by(user_id=user_id).order_by(ChatThread.created_at.desc()).all()
    
    history_data = []
    for t in threads:
        # Find the first user message to use as a title
        first_user_message = next((msg for msg in t.messages if msg.role == 'user'), None)
        title = first_user_message.content[:30] + "..." if first_user_message else "New Chat"
        
        history_data.append({
            "id": t.id,
            "title": title,
            "created_at": t.created_at.isoformat(),
            "is_public": t.is_public # Send public status to UI
        })
    return jsonify(history_data)

@app.route('/api/thread/<string:thread_id>/delete', methods=['DELETE'])
# @login_required # <-- DISABLED FOR STEP 1 TESTING
def delete_thread(thread_id):
    """ Deletes a chat thread. """
    # --- TEMPORARY FIX ---
    user_id = 1
    # --- END TEMPORARY FIX ---
    
    thread = db.session.get(ChatThread, thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), 404
        
    # TODO: When auth is on, check: if thread.user_id != current_user.id:
    if thread.user_id != user_id:
        return jsonify({"error": "Not authorized"}), 403

    try:
        db.session.delete(thread) # This deletes all its messages due to cascade
        db.session.commit()
        return jsonify({"message": "Thread deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/thread/<string:thread_id>/toggle_public', methods=['POST'])
# @login_required # <-- DISABLED FOR STEP 1 TESTING
def toggle_public(thread_id):
    """ Toggles the public/private status of a thread. """
    # --- TEMPORARY FIX ---
    user_id = 1
    # --- END TEMPORARY FIX ---

    thread = db.session.get(ChatThread, thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), 404
    
    if thread.user_id != user_id:
        return jsonify({"error": "Not authorized"}), 403

    try:
        thread.is_public = not thread.is_public # Flip the boolean
        db.session.commit()
        return jsonify({"message": "Visibility updated", "is_public": thread.is_public}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/public_threads', methods=['GET'])
def get_public_threads():
    """ Gets all threads that are marked as public. """
    threads = ChatThread.query.filter_by(is_public=True).order_by(ChatThread.created_at.desc()).all()
    
    public_data = []
    for t in threads:
        first_user_message = next((msg for msg in t.messages if msg.role == 'user'), None)
        title = first_user_message.content[:30] + "..." if first_user_message else "Public Chat"
        
        public_data.append({
            "id": t.id,
            "title": title,
            "author_username": t.user.username,
            "created_at": t.created_at.isoformat()
        })
    return jsonify(public_data)


# --- 7. AUTH & PAGE ROUTES (FOR STEP 3 & 4) ---

@app.route('/')
@login_required 
def index():
    """ The main authenticated landing page. """
    # For now, just redirect to the main chat UI
    return redirect(url_for('chat_ui'))

@app.route('/chat')
# @login_required # <-- DISABLED FOR STEP 1 TESTING
def chat_ui():
    """ Renders the main chat application UI. """
    return render_template('chat.html')

@app.route('/home')
def home_page():
    """ Renders the public 'home' page. """
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
            
    return 'This is the login page. (POST /login with username & password)'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
            
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return 'This is the register page. (POST /register with username & password)'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- 8. APP RUNNER ---

if __name__ == '__main__':
    # We do *not* run db.create_all() here.
    # We will use our 'flask create-db' command for that.
    app.run(debug=True, port=5001)