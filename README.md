# 🔎 AXIOM: AI-Powered Fact-Checking Platform

**AXIOM** is a multimodal, AI-powered fact-checking platform designed to verify information from text, URLs, images, and documents.  
This repository contains the complete plan and source code for the project.

---

## 🌐 Live Demo  
*(Link coming soon)*

---

## 🗺️ MVP Mind Map  
A visualization of the **core components** and flow of the initial Minimum Viable Product.

---

## 👤 User Management

### Authentication
- Email & Password Registration  
- Login / Logout  

### Roles
- **Logged-in User**: Can submit checks and view private history.  
- **Anonymous User**: Can submit checks, but history is not saved.  

---

## 🔎 Core Feature: Multi-Modal Fact-Checking

### User Inputs
- Text / URL Paste  
- PDF Upload  
- Image / Screenshot Upload  

### Backend Processing Flow
1. **Content Extraction**  
   - Libraries: `EasyOCR`, `PyPDF2`, `BeautifulSoup`  

2. **AI Engine - Get Evidence**  
   - Search reliable sources via **Bing News API**  

3. **AI Engine - Generate Verdict**  
   - Use a Hugging Face NLI model to compare user text against evidence  

### Output to User
- ✅ Verdict (e.g., *“Largely True”*)  
- 📊 Confidence Score  
- 📚 List of Supporting Sources  

---

## 💻 User Interface (UI)

### Pages
- **Homepage**: Submission form + recent public checks  
- **History Page**: Private history for logged-in users  
- **Auth Pages**: Login & registration forms  

---

## 🗄️ Database Schema

### Table Relationships
- **USER → FACT_CHECK** *(One-to-Many)*  
  - One user can have many fact-check records  
  - `user_id` is optional → allows anonymous checks  

- **FACT_CHECK → SOURCE** *(One-to-Many)*  
  - One fact-check can be supported by many sources  
  - Each `source` links to a specific `fact_check`  

---

## 🚀 Technology Stack

| Category        | Technology                        |
|-----------------|-----------------------------------|
| **Backend**     | Python, Flask                     |
| **Database**    | SQLAlchemy, SQLite                |
| **Frontend**    | HTML, Jinja2, Bootstrap           |
| **AI Libraries**| Hugging Face, EasyOCR             |
| **User Auth**   | Flask-Login                       |

---

## ✨ Project Phases & Features

### Phase 1: Core MVP
- 🔐 User Authentication (register, login, logout)  
- 📥 Unified Submission Engine (text, URLs, PDFs, images)  
- 🗂️ Private Fact-Check History  
- 📢 Trending Feed of recent checks  

### Phase 2: User Experience & Engagement
- 🔑 Advanced Authentication (OAuth / Google Sign-In)  
- 👤 User Profiles  
- ❤️ Social Features (like & share)  
- 💬 Commenting System  

### Phase 3: Advanced AI & Administration
- 🤖 AI Q&A on Documents (RAG)  
- 🛡️ Admin Dashboard for platform management  

---

## 🛠️ API Implementation

### RESTful Endpoints
- `GET /api/fact-checks` → Retrieve public fact-checks  
- `POST /api/check` → Create a new fact-check request  
- `PUT /api/fact-checks/<id>` → Update a fact-check  
- `DELETE /api/fact-checks/<id>` → Delete a fact-check  

### Authentication Flow
- **Sign Up** → Register with email + password  
- **Password Security** → All passwords hashed  
- **Login** → Receive auth token  
- **Logout** → End session  

---

## ⚙️ Getting Started

### Prerequisites
- Python **3.8+**  
- Pip & Virtualenv  

### Installation & Setup

Clone the repository:
```bash
git clone https://github.com/your-username/axiom.git
cd axiom
