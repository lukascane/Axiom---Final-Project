# Axiom - AI Fact-Checker
axiom-app/
├── venv/
├── app.py          # Main Flask application file
├── models.py       # Where  database tables (models) will live
├── templates/      # HTML files later
└── README.md




Axiom Project: Status Update & Checklist
This document tracks the completion of the core tasks for the Axiom project's initial setup and backend development.

1. Frontend & Project Information
My first goal was to get a basic webpage up and running and link it to my GitHub. This makes the project feel real and lets people see my progress.

Task: Put information about Phase 1 on the webpage.

Status: ✅ Done! I've changed the homepage route (/) to render index.html. I can now edit that file to add project info and a link to my GitHub.

2. GitHub Repository
I needed a public place to store my code and track all my changes. A public repo is essential for this.

Task: Start a public GitHub repository.

Status: ✅ Done! I have already successfully set this up.

3. Backend & Database Connection
The core of the app is the backend. I had to make sure my Flask application could actually connect to and create the database.

Task: Connect the backend to the database.

Status: ✅ Done! My app.py is configured to connect to and create the axiom.db file from the start.

4. API for Core Features (CRUD)
An API is how the frontend will talk to my server. I needed to build the main functions: creating, reading, and deleting data.

Task: Create an API with CRUD (Create, Read, Update, Delete) operations.

Status: ✅ Done! I've implemented the key parts:

POST (Create): Done for creating users and fact-checks.

GET (Retrieve): Done. I added the /api/history route.

DELETE: Done. I added a route to delete a user's own fact-check.

PUT (Update): This is a good feature for me to add next.

5. Anonymous User Submissions
I wanted anyone to be able to submit a fact-check, not just logged-in users. This was a key feature for the MVP.

Task: Handle anonymous user submissions.

Status: ✅ Done! I modified the /api/check route. It no longer requires a login and correctly saves submissions with or without a user_id.

6. User Authentication System
A secure login system is non-negotiable. I had to make sure users could sign up, log in, and log out safely.

Task: Implement the login/sign up flow.

Status: ✅ Done! My signup, login, and logout routes are fully functional and secure, using password hashing and session management.