# Document Question Answering System using RAG

A lightweight document question-answering system that allows users to upload a PDF or TXT document and ask questions based on its content.

This project uses a Retrieval-Augmented Generation (RAG) approach. Relevant content is retrieved from the uploaded document using TF-IDF and cosine similarity, and the retrieved context is then passed to a Groq-hosted language model to generate the answer.

## Overview

Reading through large documents to find specific information can be time-consuming.

This project provides a simple interface where users can upload a document and ask questions about its content. The system searches the uploaded document for relevant information and uses an LLM to generate a clear answer based on the retrieved context.

The main goal of this project is to understand and implement the core workflow of a RAG-based question-answering system from document ingestion to answer generation.

## Features

- Upload PDF and TXT documents
- Extract text from uploaded documents
- Split documents into smaller chunks
- Retrieve relevant content using TF-IDF
- Use cosine similarity for document retrieval
- Apply a similarity threshold to filter irrelevant results
- Generate answers using the Groq API
- Display the source document used for the answer
- Simple and responsive web interface
- Separate frontend and backend architecture
- Environment variable support for API credentials

## How It Works

The application follows a simple RAG pipeline:

```text
User uploads document
        ↓
Text extraction
        ↓
Document chunking
        ↓
TF-IDF vectorization
        ↓
User asks a question
        ↓
Cosine similarity search
        ↓
Relevant document chunks
        ↓
Groq LLM
        ↓
Final answer + source
```

## Tech Stack

### Frontend

- HTML
- CSS
- JavaScript

### Backend

- Python
- Flask
- Flask-CORS

### RAG and NLP

- Scikit-learn
- TF-IDF Vectorization
- Cosine Similarity

### Document Processing

- PyPDF

### LLM

- Groq API

### Environment Management

- python-dotenv

## Project Structure

```text
Document Question Answering System using RAG/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── documents/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.x
- Git
- A Groq API key

### Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows:

```bash
.venv\Scripts\activate
```

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file inside the `backend` directory:

```env
GROQ_API_KEY=your_groq_api_key
```

Do not commit the `.env` file to GitHub.

## Run the Backend

From the `backend` directory, run:

```bash
python app.py
```

The Flask server will start at:

```text
http://127.0.0.1:5000
```

## Run the Frontend

Open the `frontend` folder in VS Code and open `index.html` using the Live Server extension.

The frontend communicates with the Flask backend running on port `5000`.

## Using the Application

1. Open the application in your browser.
2. Select a PDF or TXT document.
3. Click **Upload Document**.
4. Wait for the document to be processed.
5. Enter a question related to the uploaded document.
6. Click **Ask**.
7. The system retrieves relevant content from the document.
8. The Groq LLM generates an answer using the retrieved context.
9. The source document is displayed with the response.

## Example

Suppose the uploaded document contains information about GATE preparation.

A user can ask:

```text
Is solving previous year questions important for GATE?
```

The system searches the document for relevant content and generates an answer based on the retrieved information.

If the requested information cannot be found, the system responds:

```text
I could not find the information in the provided documents.
```

This helps keep the responses grounded in the uploaded document instead of generating answers from unrelated information.

## RAG Implementation

This project implements a lightweight RAG pipeline.

### Document Processing

When a PDF or TXT file is uploaded, the backend extracts its text.

The extracted text is then divided into smaller chunks so that relevant sections can be retrieved efficiently.

### Retrieval

Each document chunk is converted into a TF-IDF representation using Scikit-learn.

When the user asks a question, the question is also converted into a TF-IDF vector.

Cosine similarity is then calculated between the question and the document chunks.

The most relevant chunks above the configured similarity threshold are selected as the retrieval context.

### Generation

The retrieved document chunks are provided as context to the Groq language model.

The model is instructed to answer the question using only the provided document context.

The overall process can be summarized as:

```text
Retrieval → Find relevant information

Generation → Generate an answer using the retrieved information
```

## Why RAG?

A language model by itself may generate an answer based on its general knowledge.

In this project, the RAG approach provides relevant information from the uploaded document before generating the response.

This helps the system focus on the content provided by the user and reduces the chance of generating unsupported information.

## API Endpoints

### Health Check

```text
GET /
```

Returns the current backend status.

### Upload Document

```text
POST /upload
```

Accepts a PDF or TXT document and processes it for question answering.

### Ask Question

```text
POST /chat
```

Accepts a question and returns an answer generated using the retrieved document context.

Example request:

```json
{
    "question": "What is the main topic of this document?"
}
```

Example response:

```json
{
    "answer": "The document discusses...",
    "source": "example.pdf"
}
```

## Current Limitations

The current version is a lightweight implementation designed to demonstrate the core RAG workflow.

Currently:

- One uploaded document is active at a time.
- Uploading another document replaces the currently active document data.
- Retrieval uses TF-IDF instead of semantic embeddings.
- No vector database is used.
- Scanned PDFs without extractable text may not work correctly.
- Conversation history is not persisted between sessions.
- The application is currently designed for local use.

## Future Improvements

Some planned improvements include:

- Support for multiple documents
- Semantic embeddings for improved retrieval
- Vector database integration
- Improved conversation memory
- Better PDF processing
- Document management and deletion
- User authentication
- Cloud deployment
- Streaming LLM responses
- Improved chat interface
- Better retrieval and ranking techniques

## What I Learned

Building this project helped me understand how a RAG-based application works from end to end.

Through this project, I worked with:

- Document text extraction
- Text chunking
- TF-IDF vectorization
- Cosine similarity
- Retrieval-Augmented Generation
- Prompt construction
- LLM API integration
- Flask REST APIs
- Frontend and backend communication
- Environment variables
- Git and GitHub

The project also helped me understand the difference between retrieving relevant information from documents and using an LLM to generate an answer from that information.

## Project Status

The current version is a working local implementation of a document-based question-answering system.

The core document ingestion, retrieval, and answer generation workflow is implemented and functional.

The project can be extended with semantic search, vector databases, multi-document support, authentication, and cloud deployment in future versions.

## Author

**Mallavolu Sai Ganesh**

Email:mallavolusaiganesh@gmail.com

---

