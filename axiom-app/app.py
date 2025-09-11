# --- IMPORTS ---
# Okay, so here I'm importing all the tools I need.
# Flask is for the server, render_template for HTML pages.
# request and jsonify are for handling API data.
from flask import Flask, request, jsonify, render_template

# I'm importing my database models from models.py. This is crucial.
from models import db, User, FactCheck, Source

# These are for security: hashing passwords and managing logins.
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


# --- APP SETUP ---
# This is where I create my actual Flask web app.
app = Flask(__name__)

# I need to set a secret key. This is for securing user sessions.
app.config['SECRET_key'] = 'a-super-secret-key-that-no-one-will-guess' # I should change this later.

# --- DATABASE CONFIGURATION ---
# Here, I'm telling Flask where my database file is.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///axiom.db'
# I'll turn this off to keep the console clean.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# This line officially connects my database to the app.
db.init_app(app)


# --- USER AUTHENTICATION SETUP ---
# Now I'm setting up the login manager.
login_manager = LoginManager()
login_manager.init_app(app)
# If someone who isn't logged in tries to go to a protected page,
# I'll redirect them here. Makes sense.
login_manager.login_view = 'login'

# Flask-Login needs this function to know how to find a specific user by their ID.
# It uses the ID stored in the session cookie.
@login_manager.user_loader
def load_user(user_id):
    # It just queries the User table for the matching primary key. Simple enough.
    return User.query.get(int(user_id))


# --- PAGE ROUTES ---
# This is my main homepage route.
@app.route('/')
def home():
    # My goal here is just to show the main index.html page.
    return render_template('index.html')


# --- AUTHENTICATION API ROUTES ---

# This is my endpoint for when a new user signs up.
@app.route('/signup', methods=['POST'])
def signup():
    # First, I grab the email and password they sent.
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # I must check if the email is already in use.
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email address already registered"}), 409

    # Now, I'll hash the password. I should never, ever store it as plain text.
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    # With the hashed password, I can create the new user and save them to the DB.
    new_user = User(email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!"}), 201

# This route is for logging in an existing user.
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # I need to find the user by their email first.
    user = User.query.filter_by(email=email).first()

    # My logic here is to check two things: does the user exist, AND is the password correct?
    # The `check_password_hash` function handles the secure comparison for me.
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    # If everything checks out, I log them in. Flask-Login takes care of the session.
    login_user(user)
    return jsonify({"message": "Logged in successfully", "user_id": user.id}), 200

# This is my logout route. It has to be protected so only logged-in users can access it.
@app.route('/logout')
@login_required
def logout():
    logout_user() # This function from Flask-Login clears the session.
    return jsonify({"message": "Logged out successfully"}), 200


# --- CORE FEATURE API ROUTES (CRUD) ---

# This is my API for creating a new fact-check.
@app.route('/api/check', methods=['POST'])
def create_check():
    data = request.get_json()
    claim = data.get('claim')
    user_id_to_store = None # I'll start with None for anonymous users.

    # I have to make sure they actually sent a claim.
    if not claim:
        return jsonify({"error": "Claim text is required"}), 400

    # My logic for handling both user types: if the current user is logged in,
    # I'll grab their ID. Otherwise, it stays None.
    if current_user.is_authenticated:
        user_id_to_store = current_user.id

    # Now I create the record, linking it to a user ID if one exists.
    new_check = FactCheck(claim_text=claim, user_id=user_id_to_store)

    db.session.add(new_check)
    db.session.commit()

    return jsonify({"message": "Fact check submitted!", "check_id": new_check.id}), 201

# This route is for getting a user's own history. (Read part of CRUD)
@app.route('/api/history', methods=['GET'])
@login_required # A user should only be able to see their own history.
def get_history():
    # I'll find all the checks in the database that match the current user's ID.
    user_checks = FactCheck.query.filter_by(user_id=current_user.id).all()
    
    # I need to format this data nicely into a list before sending it as JSON.
    history_list = []
    for check in user_checks:
        history_list.append({
            "id": check.id,
            "claim": check.claim_text,
            "verdict": check.verdict # This will be null for now, but I'll add it.
        })
    return jsonify(history_list), 200

# This route is for deleting a fact-check. (Delete part of CRUD)
@app.route('/api/check/<int:check_id>', methods=['DELETE'])
@login_required # Must be logged in to delete.
def delete_check(check_id):
    # I'll find the specific check they want to delete by its ID.
    check_to_delete = FactCheck.query.get(check_id)

    # What if the ID doesn't exist? I need to handle that.
    if not check_to_delete:
        return jsonify({"error": "Fact check not found"}), 404

    # This is a critical security check. I must verify that the person deleting the check
    # is the same person who created it.
    if check_to_delete.user_id != current_user.id:
        return jsonify({"error": "You are not authorized to delete this item"}), 403

    # If they are the owner, I can proceed with the deletion.
    db.session.delete(check_to_delete)
    db.session.commit()

    return jsonify({"message": "Fact check deleted successfully"}), 200


# --- RUN THE APP ---
# This `if` statement makes sure the server only runs when I execute this file directly.
if __name__ == '__main__':
    # I need to create the database tables from my models before running the app.
    # The `with app.app_context()` makes sure the app is ready for this.
    with app.app_context():
        db.create_all()
    # Okay, time to run the server. Debug mode is on so it reloads automatically.
    app.run(debug=True)

