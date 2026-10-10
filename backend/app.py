
import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq


# Load environment variables

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# Create Flask app

app = Flask(__name__)

CORS(app)


# Create Groq client

client = Groq(
    api_key=GROQ_API_KEY
) if GROQ_API_KEY else None


# Configure upload folder

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "documents"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Configure retrieval threshold

SIMILARITY_THRESHOLD = 0.10

NOT_FOUND_ANSWER = (
    "I could not find the information in the provided documents."
)


# Store document data

vectorizer = TfidfVectorizer(
    sublinear_tf=True
)

chunk_vectors = None

document_chunks = []

chunk_sources = []


# Extract text from uploaded document

def extract_text(file_path):

    text = ""

    if file_path.lower().endswith(".txt"):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()

    elif file_path.lower().endswith(".pdf"):

        reader = PdfReader(file_path)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"

    return text


# Split document text into chunks

def split_text(
    text,
    chunk_size=500,
    overlap=100
):

    chunks = []

    step = chunk_size - overlap

    for i in range(
        0,
        len(text),
        step
    ):

        chunk = text[
            i:i + chunk_size
        ]

        if chunk.strip():

            chunks.append(chunk)

    return chunks


# Create TF-IDF vectors for document chunks

def create_vectors(
    chunks,
    source
):

    global chunk_vectors
    global document_chunks
    global chunk_sources

    document_chunks = chunks

    chunk_sources = [
        source
        for _ in chunks
    ]

    chunk_vectors = vectorizer.fit_transform(
        document_chunks
    )


# Retrieve relevant chunks

def retrieve_chunks(
    query,
    top_k=3
):

    if chunk_vectors is None:

        return []

    query_vector = vectorizer.transform(
        [query]
    )

    similarities = cosine_similarity(
        query_vector,
        chunk_vectors
    ).flatten()

    ranked_indices = similarities.argsort()[::-1]

    selected_chunks = []

    for index in ranked_indices[:top_k]:

        score = float(
            similarities[index]
        )

        if score < SIMILARITY_THRESHOLD:

            break

        selected_chunks.append({
            "content": document_chunks[index],
            "score": score,
            "source": chunk_sources[index]
        })

    return selected_chunks


# Build RAG prompt

def build_prompt(
    query,
    retrieved_chunks
):

    context_parts = []

    for item in retrieved_chunks:

        context_parts.append(
            item["content"]
        )

    context = "\n\n".join(
        context_parts
    )

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using only the information
explicitly supported by the document context.

If the context does not contain enough information
to answer the question, respond with exactly:
{NOT_FOUND_ANSWER}

Do not use your general knowledge.
Do not invent facts.
Do not guess or infer missing information.
If only part of the question is answered by the context,
answer only that supported part.

Document context:
{context}

User question:
{query}
"""

    return prompt


# Generate answer using Groq

def ask_groq(prompt):

    if client is None:

        raise RuntimeError(
            "GROQ_API_KEY is missing from the environment."
        )

    completion = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )

    return completion.choices[0].message.content.strip()


# Check whether the answer indicates missing information

def is_not_found_answer(answer):

    normalized_answer = answer.lower().strip()

    normalized_answer = normalized_answer.replace(
        "**",
        ""
    ).replace(
        "*",
        ""
    ).replace(
        "`",
        ""
    ).strip()

    not_found_phrases = [
        NOT_FOUND_ANSWER.lower(),
        "the information is not available in the provided documents",
        "the provided documents do not contain this information",
        "the document does not provide this information",
        "the context does not contain enough information"
    ]

    return any(
        phrase in normalized_answer
        for phrase in not_found_phrases
    )


# Check backend status

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return jsonify({
        "message": "RAG Document QA Backend is running!"
    })


# Handle document upload

@app.route(
    "/upload",
    methods=["POST"]
)
def upload_document():

    if "file" not in request.files:

        return jsonify({
            "error": "No file uploaded"
        }), 400

    file = request.files["file"]

    if file.filename == "":

        return jsonify({
            "error": "No file selected"
        }), 400

    filename = os.path.basename(
        file.filename
    )

    allowed_extensions = {
        ".pdf",
        ".txt"
    }

    file_extension = os.path.splitext(
        filename
    )[1].lower()

    if file_extension not in allowed_extensions:

        return jsonify({
            "error": "Only PDF and TXT files are allowed"
        }), 400

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    try:

        file.save(file_path)

        text = extract_text(
            file_path
        )

    except Exception as error:

        app.logger.exception(
            "Document processing failed"
        )

        return jsonify({
            "error": "Could not read the document. Please check the file."
        }), 400

    if not text.strip():

        return jsonify({
            "error": "Could not extract text from the document"
        }), 400

    chunks = split_text(
        text
    )

    if not chunks:

        return jsonify({
            "error": "Could not create document chunks"
        }), 400

    create_vectors(
        chunks,
        filename
    )

    return jsonify({
        "message": "Document uploaded and processed successfully",
        "file_name": filename,
        "chunks": len(chunks)
    }), 200


# Handle chat questions

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "error": "No data provided"
        }), 400

    query = data.get(
        "question",
        ""
    )

    if not isinstance(query, str):

        return jsonify({
            "error": "Question must be text"
        }), 400

    query = query.strip()

    if not query:

        return jsonify({
            "error": "Question is required"
        }), 400

    retrieved_chunks = retrieve_chunks(
        query,
        top_k=3
    )

    if not retrieved_chunks:

        return jsonify({
            "answer": NOT_FOUND_ANSWER,
            "source": None
        }), 200

    try:

        prompt = build_prompt(
            query,
            retrieved_chunks
        )

        answer = ask_groq(
            prompt
        )

    except Exception:

        app.logger.exception(
            "Answer generation failed"
        )

        return jsonify({
            "error": "Could not generate an answer. Please try again."
        }), 500

    # Do not show a source when the answer is not found

    if is_not_found_answer(answer):

        return jsonify({
            "answer": NOT_FOUND_ANSWER,
            "source": None
        }), 200

    sources = sorted({
        item["source"]
        for item in retrieved_chunks
    })

    return jsonify({
        "answer": answer,
        "source": ", ".join(sources) if sources else None
    }), 200


# Run Flask server

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )
