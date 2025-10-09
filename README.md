3.10.2025 

The User History Page 
The Chat Page (chat.html)
This is the most important page of my application. It needs to be smart enough to handle several different situations: starting a new chat, viewing an old one, and showing a read-only view for public conversations.

My Explanation of the Code:

Structure: The layout is consistent with my other pages, featuring the main navigation bar. The core of the page is a chat window that will display messages and an input area at the bottom for typing.

Jinja2 Templating (The Magic): I'm using special Flask template tags like {% if is_owner %} and {{ thread_id|tojson }}.

{{ thread_id|tojson }} and {{ is_owner|tojson }} are how my Python backend securely passes data (like the current conversation ID and whether I'm the owner) to my frontend JavaScript.

{% if is_owner %} is a powerful feature that lets me change the HTML before it even gets to the browser. I'm using it to completely hide the message input box for users who are not the owner of the conversation, creating a "read-only" mode for public chats, exactly as I designed in my diagram.

JavaScript Logic (The Brains): The <script> at the bottom contains the complete client-side application for the chat.

startNewThread(): If I navigate to the /chat URL, the threadId will be null. The script detects this and automatically calls my /api/chat/start endpoint. After my backend creates a new thread, the script reloads the page to the new URL (/chat/1, for example), creating a seamless experience.

loadHistory(): If a threadId is present, this function is called instead. It fetches the conversation history from my /api/chat/<thread_id> endpoint and displays all the messages.

sendMessage(): When I click the send button, this function instantly adds my message to the chat window (for a fast UI), shows a "..." loading indicator, and sends my message to the backend. When the AI responds, it replaces the "..." with the real answer.

handleConversationLimit(): This function checks if I've reached the 5-message limit and will hide the input box, showing a "Conversation limit reached" message, which fulfills my token management strategy. 

(history.html)
This is my private dashboard. After I log in, this is where I will see a list of all my past conversations. I will also add the buttons here to allow me to delete a conversation or share it publicly, just like I planned in my diagram.

My Explanation of the Code:

Structure: I'm keeping the layout consistent with my home page, with the same navigation bar for a familiar user experience. The main area has a title and a container (div id="history-container") where my JavaScript will load my personal chat history.

JavaScript Logic: This page is highly interactive.

loadHistory(): As soon as this page loads, this function is called. It makes a fetch request to my /api/history endpoint. Because this is a protected route, the browser will automatically send my login cookie, so the backend knows to only send back my threads.

Dynamic List & Buttons: The script then builds an HTML card for each of my conversations. I'm making sure to include a red "Delete" button and a green "Share Publicly" button on each card. The share button will change to yellow and say "Make Private" if the chat is already public.

deleteThread(threadId): This function handles the delete feature. It first shows a confirmation box to make sure I don't delete something by accident. If I confirm, it sends a DELETE request to my /api/thread/<thread_id> endpoint. On a successful response, it instantly removes the card from the page, making the UI feel fast.

togglePublic(threadId, button): This function manages sharing. It sends a POST request to my /api/thread/<thread_id>/toggle_public endpoint. When my backend confirms the change, the script updates the button's text and color to show the new public or private status.

I'll build the public landing page for my application where anyone can see the conversations that have been shared.

My Explanation of the Code:

Structure: I'm creating a simple and clean layout with a navigation bar at the top that links to "My History" and "New Chat". The main part of the page has a title and a container (div id="threads-container") where I'll load the public chats.

JavaScript Logic: The <script> tag at the bottom is the engine of this page. When the page loads (DOMContentLoaded), it will automatically make a fetch call to my /api/public_threads endpoint. It will then dynamically build an HTML card for each public conversation it receives from the server, showing the title, author, and date. This makes the page feel live and interactive.

My Action:
I will now create a new file named home.html inside my axiom-app/templates folder and add the following code.


My Step-by-Step Implementation Plan
My goal is to build out the full user experience from my diagram. This means creating new pages for public chats and my private history, and adding more features to the chat page itself. This requires a major update to my app.py file to handle the new logic and the creation of new HTML files for the frontend.

Step 1: Upgrading My Backend (app.py)
First, I need to update my main application file, app.py, to support all the new features.

My Explanation of the Changes:

New HTML Page Routes: My application needs to know how to serve the new pages. I'll add routes like /home, /history, and /chat/<thread_id> that will render the corresponding HTML templates. I'll also add routes for the login and signup pages so users don't just see a JSON error if they aren't logged in.

Enhanced API Endpoints: To power these new pages, I need new API endpoints. I will create:

GET /api/public_threads: This will fetch all conversations that users have marked as public, which is exactly what my "home page" needs.

GET /api/history: This will fetch all threads belonging only to the currently logged-in user for my "facts list page."

DELETE /api/thread/<thread_id>: This fulfills the requirement that "users can delete a fact/thread if they want." I'll add a security check to ensure users can only delete their own threads.

POST /api/thread/<thread_id>/toggle_public: This implements the feature where "users can make them private by clicking a button." It will flip the is_public flag in the database.

Improved User Flow: I'll update my /login API so that after a successful login, it tells the browser to redirect to the user's history page, creating a smoother experience.

My Action:
I will now replace the entire content of my axiom-app/app.py file with this new, complete version.

Step 2: Creating My Frontend Pages
Now that my backend is ready, I need to build the user interface. I'll create two new HTML files and update my existing chat.html.

My Action:
I will now create home.html and history.html in my axiom-app/templates folder and replace the content of chat.html.

Final Step: Test the Full Experience
Explanation: The database schema has changed, so my old database file is now out of date. I need to delete it so Flask can create a new one with the correct structure.

Your Action:

Stop your Flask server if it's running (Ctrl + C).

In your axiom-app folder, delete the axiom.db file.

Restart your server: python3 app.py.

Explanation: Now I can test the full user flow in my browser.

Your Action:

Go to http://127.0.0.1:5000. You should be redirected to the public home page.

Click on "My History" and you will be taken to the login page.

Sign up for a new account and then log in.

You will be redirected to your (empty) history page. Click "New Chat" to start a conversation.

After chatting, go back to your "My History" page. You will see your new conversation listed. You can now use the buttons to delete it or make it public. If you make it public, it will appear on the home page for everyone to see.



2.10.2025 
High-Level Functionalities
we will build the complete backend logic and all the necessary frontend pages to bring your diagram to life.
Explanation: This is a major update. We will completely replace your app.py with a new version that includes all the routes to serve the HTML pages (/home, /history, /chat) and the API endpoints that provide data for them. We will also create two brand-new HTML files (home.html, history.html) and significantly upgrade your chat.html to be fully interactive.

Technical Design - Database Schema
My diagram correctly identifies that the Threads table needs an is_public field to manage visibility. Your current models.py on GitHub is missing this.

25.09.2025:

Step 1: Evolving the Database for Conversations
My first action was to completely redesign the database structure to properly support multi-turn conversations.

Action Taken:
I replaced my old Fact model with two new, interconnected models: ChatThread and ChatMessage.

Rationale:

Why the change? My original single-table design was insufficient because a conversation is more than one request and response; it's a collection of linked messages. Storing each message as an independent "fact" would make it impossible to retrieve a coherent conversation history.

Why a ChatThread table? This table acts as a container. Each time a user starts a new conversation, a new thread is created and linked to their user_id. This was a core requirement and allows me to group all related messages logically.

Why a ChatMessage table? This table stores every individual message from both the user and the assistant. Crucially, each message has a thread_id, which links it back to its parent conversation. This structure makes it simple and efficient to query the database for the complete history of any given chat.

Step 2: Rebuilding the Backend for a Conversational Flow
With the new database structure in place, I rewrote the core application logic in app.py to handle the lifecycle of a chat.

Action Taken:
I implemented three new API endpoints and integrated a token management strategy directly into the application logic.

Rationale:

Why new API endpoints? The user's interaction with a chatbot is a sequence of events. I designed the API to mirror this logical flow:

POST /api/chat/start: A user must first create a conversation thread before they can send messages.

POST /api/chat/<thread_id>/message: All subsequent messages are sent to this endpoint, ensuring they are saved to the correct conversation.

GET /api/chat/<thread_id>: This allows the user (and the application) to retrieve the full history of a specific conversation.

Why I Chose My Token Management Strategy: Preserving history is expensive, as the context sent to the AI grows with every message. I decided that for the MVP, the best balance between user experience and cost control was to limit the number of messages per thread (to 5 user questions).

This approach guarantees the highest possible quality of AI responses because the model always receives the full, untruncated context of the conversation.

It also creates a predictable upper limit on token costs for any single conversation, which is a critical consideration for a real-world application. I also added a character limit on user input as another simple safeguard against excessive token usage.

Step 3: Ensuring Reliability Through Rigorous Testing
After implementing these significant changes, I performed a full suite of tests to verify that every part of the new system works as intended.

Action Taken:
I conducted a clean-slate test by deleting the old database, restarting the server to generate the new schema, and using curl to simulate a complete user journey.

This update will address your primary goal and your chosen token-management strategy.

Key Features Implemented:

New API Endpoints: /api/chat/start, /api/chat/<thread_id>/message, and /api/chat/<thread_id>.

Full History Context: The entire chat history is fetched and prepared for the AI on every new message.

Token/Cost Management:

Conversations are limited to 5 user questions (10 total messages).

The length of a user's submitted message is limited to 1000 characters.


Rationale:

Why delete the database? My changes to models.py were a "breaking change." The new application code would not be able to read the old database structure, so starting fresh was essential to prevent errors and ensure the new ChatThread and ChatMessage tables were created correctly.

Why use curl? Without a frontend interface, curl allows me to act as the browser and directly test each API endpoint in the correct sequence. My test plan confirmed that a user can successfully sign up, log in, start a thread, exchange several messages with the AI (with the server correctly remembering the context), and retrieve the conversation history. This proves that the entire backend system is fully functional.



23.09.2025:


I'm currently focused on the models.py file, adding the ChatThread and ChatMessage tables. These will serve as the foundation for storing and managing conversation histories, a crucial step in the process. My next step will be to create a new engine.py file to handle more of the application logic.

Building Chat Functionality

I'm now integrating the chatbot API endpoints into app.py, which is going to replace the previous fact-checking mechanisms. I've designed routes for starting new chats, sending messages, and retrieving the conversation history. In addition, I will create a guide for testing the new chatbot features using curl commands. This will ensure each part of the implementation functions as expected.# 🧠 Axiom: AI-Powered Fact-Checking Platform

Building Chat Functionality

I'm now integrating the chatbot API endpoints into app.py, which is going to replace the previous fact-checking mechanisms. I've designed routes for starting new chats, sending messages, and retrieving the conversation history. In addition, I will create a guide for testing the new chatbot features using curl commands. This will ensure each part of the implementation functions as expected.\

previosly:

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Flask](https://img.shields.io/badge/flask-2.0+-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)](../../issues)

**Axiom** is a multimodal, AI-powered fact-checking platform designed to verify information from text and documents.  
This repository contains the complete plan and source code for the project.

🔗 **Live Demo**: [your-axiom-live-url.com](https://your-axiom-live-url.com)

---

## 📈 Project Status
- **Author**: [lukascane](https://github.com/lukascane)  
- **Start Date**: September 11, 2025  

### Progress Timeline
- **2025-09-11** → Project inception, core MVP definition, and technology stack selection  

---

## 🗺️ MVP Mind Map
A visualization of the **core components** and flow of the initial Minimum Viable Product (MVP).

---

## 👤 User Management

### Authentication
- Email & Password Registration  
- Login / Logout  

### Roles
- **Logged-in User** → Can submit checks & view private history  
- **Anonymous User** → Can submit checks, but history is not saved  

---

## 🔎 Core Feature: Multi-Modal Fact-Checking

### User Inputs (MVP Scope)
- 📝 Text / URL Paste  
- 📄 PDF Upload  

### Backend Processing Flow
1. **Content Extraction** → `PyPDF2`, `BeautifulSoup`  
2. **AI Engine - Get Evidence** → Search reliable sources via **Bing News API**  
3. **AI Engine - Generate Verdict** → Hugging Face NLI model compares text vs. evidence  

### Output to User
- ✅ Verdict (e.g., *“Largely True”*)  
- 📊 Confidence Score  
- 📚 List of Supporting Sources  

---

## 💻 User Interface (UI)

### Pages
- **Homepage** → Submission form + recent public checks  
- **History Page** → Private fact-check history for logged-in users  
- **Auth Pages** → Login & registration forms  

---

## 🗄️ Database Schema

### Table Relationships
- **USER → FACT_CHECK** *(One-to-Many)*  
  - One user can have many fact-checks  
  - `user_id` is optional (nullable) → allows anonymous submissions  

- **FACT_CHECK → SOURCE** *(One-to-Many)*  
  - One fact-check can be backed by multiple sources  
  - Each `source` links to its `fact_check`  

---

## 🚀 Technology Stack

| Category        | Technology                        |
|-----------------|-----------------------------------|
| **Backend**     | Python, Flask                     |
| **Database**    | SQLAlchemy, SQLite                |
| **Frontend**    | HTML, Jinja2, Bootstrap           |
| **AI Libraries**| Hugging Face, PyPDF2              |
| **User Auth**   | Flask-Login                       |

---

## ✨ Project Phases & Features

### Phase 1: Core MVP *(Current Focus)*
- 🔐 User Authentication (register, login, logout)  
- 📥 Unified Submission Engine (text + PDFs)  
- 🗂️ Private Fact-Check History (for logged-in users)  
- 📢 Trending Feed (recent public checks)  

### Phase 2: User Experience & Engagement *(Future)*
- 🔑 Advanced Authentication (OAuth, Google Sign-In)  
- 👤 User Profiles  
- ❤️ Social Features (like & share)  
- 💬 Commenting System  

### Phase 3: Advanced AI & Administration *(Future)*
- 🤖 AI Q&A on Documents (RAG)  
- 🛡️ Admin Dashboard  

---

## 🛠️ API Implementation

### RESTful Endpoints
- `GET /api/fact-checks` → Retrieve public fact-checks  
- `POST /api/check` → Create a new fact-check request  
- `PUT /api/fact-checks/<id>` → Update a specific fact-check  
- `DELETE /api/fact-checks/<id>` → Delete a fact-check  

### Authentication Flow
- **Sign Up** → Register with email & password  
- **Password Security** → Hash before storage  
- **Login** → Auth token issued  
- **Logout** → End session  

---

## ⚙️ Getting Started

### Prerequisites
- Python **3.8+**  
- Pip & Virtualenv  

### Installation & Setup

Clone the repository:
```bash
git clone https://github.com/lukascane/Axiom.git
cd Axiom
