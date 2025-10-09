from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Thread, Message # This now correctly matches models.py
from ai_service import get_ai_response

# --- APP SETUP ---
app = Flask(__name__)
CORS(app) # Enable Cross-Origin requests for your React app

# --- DATABASE CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- API ENDPOINTS ---

# Endpoint to create a new thread
@app.route('/api/threads', methods=['POST'])
def create_thread():
    data = request.json
    user_id = 1 # Hardcoding user_id to 1 for simplicity
    
    new_thread = Thread(
        user_id=user_id,
        title=data.get('title', 'New Conversation'),
        is_public=data.get('is_public', True)
    )
    db.session.add(new_thread)
    db.session.commit()
    return jsonify(new_thread.to_dict()), 201

# Endpoint to send a message and get an AI response
@app.route('/api/threads/<int:thread_id>/messages', methods=['POST'])
def send_message(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    user_message_content = request.json.get('content')

    if not user_message_content:
        return jsonify({"error": "Message content is required"}), 400

    user_message = Message(thread_id=thread_id, content=user_message_content, role='user')
    db.session.add(user_message)
    db.session.commit()

    history = Message.query.filter_by(thread_id=thread_id).order_by(Message.created_date).all()
    ai_response_content = get_ai_response(history)

    ai_message = Message(thread_id=thread_id, content=ai_response_content, role='assistant')
    db.session.add(ai_message)
    db.session.commit()

    return jsonify(ai_message.to_dict())

# Endpoint to fetch all messages for a specific thread
@app.route('/api/threads/<int:thread_id>', methods=['GET'])
def get_thread_messages(thread_id):
    messages = Message.query.filter_by(thread_id=thread_id).order_by(Message.created_date).all()
    return jsonify([msg.to_dict() for msg in messages])

# Endpoint to fetch all public threads
@app.route('/api/threads/public', methods=['GET'])
def get_public_threads():
    threads = Thread.query.filter_by(is_public=True).order_by(Thread.created_date.desc()).all()
    return jsonify([t.to_dict() for t in threads])

# --- RUN THE APP ---
if __name__ == '__main__':
    with app.app_context():
        # This will create the database file and tables if they don't exist
        db.create_all()
    app.run(debug=True, port=5001)
