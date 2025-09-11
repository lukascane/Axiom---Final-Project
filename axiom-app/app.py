# --- IMPORTS ---
# I need these tools to make my web app work.
from flask import Flask, request, jsonify, render_template

# These are my database models from the other file.
from models import db, User, FactCheck, Source

# Werkzeug is a tool that helps with password security.
from werkzeug.security import generate_password_hash, check_password_hash

# Flask-Login will manage the user's session.
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


# --- APP SETUP ---
# This line creates my web application.
app = Flask(__name__)

# --- CONFIGURATION ---
# THIS IS THE LINE I NEED TO ADD.
# The secret key is essential for creating secure user sessions.
# I need to set this to a long, random, and secret string.
app.config['SECRET_KEY'] = 'a-super-secret-key-that-no-one-will-guess'

# I'm telling my app where to find the database. It'll be a file called 'axiom.db'.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///axiom.db'
# This is just to turn off a feature I don't need, which keeps my console clean.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# This connects my database to my Flask app.
db.init_app(app)


# --- USER AUTHENTICATION SETUP ---
# This sets up the login manager.
login_manager = LoginManager()
login_manager.init_app(app)
# If a user tries to access a protected page but isn't logged in,
# I'll send them to the 'login' page.
login_manager.login_view = 'login'

# This function is required by Flask-Login. It's how it loads a user
# from the database based on their ID, which is stored in the session cookie.
@login_manager.user_loader
def load_user(user_id):
    # It finds the user by their primary key (ID).
    return User.query.get(int(user_id))


# --- PAGE ROUTES ---
# This is my homepage. It will show the index.html file.
@app.route('/')
def home():
    # My app will look for 'index.html' inside a folder named 'templates'.
    return render_template('index.html')


# --- AUTHENTICATION API ROUTES ---

# This route handles user registration.
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # I check if a user with this email already exists to avoid duplicates.
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email address already registered"}), 409

    # I will never store the password directly. Instead, I create a secure "hash".
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    # Now I create the new user with the hashed password.
    new_user = User(email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!"}), 201


# This route handles user login.
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # I look for a user with the provided email.
    user = User.query.filter_by(email=email).first()

    # I check if the user exists AND if the password they provided matches the stored hash.
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
    logout_user() # This clears the user's session.
    return jsonify({"message": "Logged out successfully"}), 200


# --- CORE FEATURE API ROUTES ---

# This is the API endpoint for submitting a fact-check.
# I removed @login_required to allow anonymous submissions.
@app.route('/api/check', methods=['POST'])
def create_check():
    data = request.get_json()
    claim = data.get('claim')
    user_id = None # Default to None for anonymous users

    # I make sure the user actually sent some text to check.
    if not claim:
        return jsonify({"error": "Claim text is required"}), 400

    # I check if a user is logged in.
    if current_user.is_authenticated:
        user_id = current_user.id

    # I create a new FactCheck record.
    # This will be linked to a user_id if they're logged in, otherwise it will be null.
    new_check = FactCheck(claim_text=claim, user_id=user_id)

    db.session.add(new_check)
    db.session.commit()

    return jsonify({"message": "Fact check submitted!", "check_id": new_check.id}), 201

# This route gets the history for the currently logged-in user.
@app.route('/api/history', methods=['GET'])
@login_required
def get_history():
    # I get all checks where the user_id matches the logged-in user.
    user_checks = FactCheck.query.filter_by(user_id=current_user.id).all()
    # I need to convert the list of objects into a list of dictionaries to send as JSON.
    history = [
        {"id": check.id, "claim_text": check.claim_text, "verdict": check.verdict, "user_id": check.user_id}
        for check in user_checks
    ]
    return jsonify(history), 200


# This route allows a user to delete one of their own fact-checks.
@app.route('/api/check/<int:check_id>', methods=['DELETE'])
@login_required
def delete_check(check_id):
    # I find the check the user wants to delete.
    check_to_delete = FactCheck.query.get(check_id)

    # I make sure the check actually exists.
    if not check_to_delete:
        return jsonify({"error": "Fact check not found"}), 404

    # This is a critical security check. I make sure the person trying to delete the
    # check is the same person who created it.
    if check_to_delete.user_id != current_user.id:
        return jsonify({"error": "You are not authorized to delete this item"}), 403 # 403 means "Forbidden"

    # If everything is okay, I delete it from the database.
    db.session.delete(check_to_delete)
    db.session.commit()

    return jsonify({"message": "Fact check deleted successfully"}), 200


# --- RUN THE APP ---
# This part of the script only runs if I execute `python app.py` directly.
if __name__ == '__main__':
    with app.app_context():
        # This creates the database tables if they don't exist yet.
        db.create_all()
    # This starts my web server.
    app.run(debug=True)
