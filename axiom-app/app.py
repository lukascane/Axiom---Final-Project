# In app.py
from flask import Flask, request, jsonify
from models import db, User, FactCheck, Source

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
# Use SQLite for simplicity. The database will be a file named 'axiom.db'.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///axiom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# --- A SIMPLE HOMEPAGE ROUTE ---
@app.route('/')
def home():
    # We'll put phase 1 info here later in an HTML file
    return "Welcome to Axiom! Phase 1: Backend Setup."

# --- A placeholder for your API ---
# This is where we will build the CRUD operations
@app.route('/api/check', methods=['POST'])
def create_check():
    # Get the data sent from the user
    data = request.get_json()
    claim = data.get('claim')

    if not claim:
        return jsonify({"error": "Claim text is required"}), 400

    # For now, we won't link to a user. We'll add that later.
    new_check = FactCheck(claim_text=claim, user_id=None) # Example for anonymous

    # Add to database
    db.session.add(new_check)
    db.session.commit()

    return jsonify({"message": "Fact check submitted!", "id": new_check.id}), 201


# --- CREATE THE DATABASE ---
# This block runs only when you execute `python app.py` directly
if __name__ == '__main__':
    with app.app_context():
        # This line creates the tables based on your models.py
        db.create_all()
    app.run(debug=True)