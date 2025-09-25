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
