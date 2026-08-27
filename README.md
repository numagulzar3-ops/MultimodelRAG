# 🤖 MultiModel RAG

A document-based AI question-answering system that allows users to upload **PDF and DOCX files** and ask questions about their contents.

The application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant sections from the uploaded document and generate grounded answers using Google's Gemini model.

## 🌐 Live Demo

**Frontend:**
https://multimodel-rag.vercel.app/

**Backend API:**
https://multimodel-rag-api.onrender.com/

## ✨ Features

* 📄 Upload PDF and DOCX documents
* 🔍 Automatically extract and process document content
* ✂️ Split documents into smaller chunks
* 🧠 Generate semantic embeddings
* 🔎 Perform similarity search using FAISS
* 🤖 Generate answers using Google Gemini
* 📚 Display retrieved document sources
* 💬 Interactive chat interface
* ⚡ React + Vite frontend
* 🚀 Deployed frontend and backend

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │      User            │
                    │   Web Browser        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   React + Vite       │
                    │      Vercel          │
                    └──────────┬───────────┘
                               │
                               │ HTTP API
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │       Render         │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌──────────────────┐        ┌──────────────────┐
       │   Unstructured   │        │   Embedding      │
       │ Document Parsing │        │      Model       │
       └────────┬─────────┘        └────────┬─────────┘
                │                           │
                ▼                           ▼
       ┌──────────────────┐        ┌──────────────────┐
       │ Document Chunks  │───────▶│      FAISS       │
       └──────────────────┘        │ Vector Search    │
                                   └────────┬─────────┘
                                            │
                                            ▼
                                   ┌──────────────────┐
                                   │  Google Gemini   │
                                   │  Answer Gen.     │
                                   └──────────────────┘
```

## 🔄 How It Works

### 1. Upload Document

The user uploads a PDF or DOCX file through the React frontend.

### 2. Document Processing

The FastAPI backend receives the document and uses **Unstructured** to extract its content.

### 3. Chunking

The extracted content is divided into smaller chunks so that relevant sections can be retrieved efficiently.

### 4. Embeddings

Each chunk is converted into a numerical vector using a sentence-transformer embedding model.

### 5. Vector Search

The embeddings are stored in **FAISS** and similarity search is performed whenever the user asks a question.

### 6. Retrieval

The most relevant document chunks are retrieved based on the user's question.

### 7. Generation

The retrieved context is provided to **Google Gemini**, which generates an answer grounded in the uploaded document.

### 8. Response

The answer and retrieved source chunks are returned to the React frontend.

## 🛠️ Tech Stack

### Frontend

* React
* Vite
* JavaScript
* CSS

### Backend

* Python
* FastAPI
* Uvicorn

### RAG Pipeline

* Unstructured
* Sentence Transformers
* FAISS
* Google Gemini

### Deployment

* Vercel — Frontend
* Render — Backend
* GitHub — Source Control

## 📁 Project Structure

```text
MultimodelRAG/
│
├── backend/
│   ├── main.py
│   └── rag_engine.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── vite.config.js
│
├── uploads/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/numagulzar3-ops/MultimodelRAG.git
cd MultimodelRAG
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**macOS/Linux**

```bash
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API Key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Never commit your API key to GitHub.

### 5. Start the backend

```bash
uvicorn backend.main:app --reload
```

The API will run at:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

### 6. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will normally run at:

```text
http://localhost:5173
```

## 🔌 API Endpoints

### `GET /`

Checks whether the API is running.

### `POST /upload`

Uploads and processes a PDF or DOCX document.

### `POST /ask`

Accepts a question and returns an AI-generated answer based on the uploaded document.

Example request:

```json
{
  "question": "What is String[] args in Java?"
}
```

## 🔐 Environment Variables

The backend requires:

```env
GEMINI_API_KEY=your_api_key_here
```

API keys should be stored in environment variables and **never committed to the repository**.

## 📸 Example Workflow

```text
Upload Document
      ↓
Document Processing
      ↓
Text Extraction
      ↓
Chunking
      ↓
Embedding Generation
      ↓
FAISS Indexing
      ↓
Ask Question
      ↓
Similarity Search
      ↓
Relevant Chunks
      ↓
Gemini
      ↓
Grounded Answer + Sources
```

## 🎯 Project Goal

The goal of this project is to demonstrate how a modern **Retrieval-Augmented Generation system** can combine document processing, semantic search, vector databases, and generative AI to create an interactive document assistant.

## 👨‍💻 Author

**Numa Gulzar**

Computer Science & Engineering

---

⭐ If you found this project useful, consider giving the repository a star!
