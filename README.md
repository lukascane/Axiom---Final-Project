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
