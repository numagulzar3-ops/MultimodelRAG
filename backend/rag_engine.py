import os

import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

from unstructured.partition.docx import partition_docx
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

from google import genai


# ============================================================
# 1. GEMINI CLIENT
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is not set."
    )

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# 2. EMBEDDING MODEL
# ============================================================

model = None


def get_embedding_model():

    global model

    if model is None:

        print("\nLoading embedding model...")

        model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("Embedding model loaded.")

    return model


# ============================================================
# 3. GLOBAL RAG STATE
# ============================================================

texts = []
index = None
chat_history = []


# ============================================================
# 4. PROCESS DOCUMENT
# ============================================================

def process_document(file_path):

    global texts
    global index
    global chat_history

    print("\nProcessing document:")
    print(file_path)

    # --------------------------------------------------------
    # Load document
    # --------------------------------------------------------

    if file_path.lower().endswith(".docx"):

        elements = partition_docx(
            filename=file_path
        )

    elif file_path.lower().endswith(".pdf"):

        elements = partition_pdf(
            filename=file_path
        )

    else:

        raise ValueError(
            "Unsupported file type. Please upload a PDF or DOCX file."
        )

    # --------------------------------------------------------
    # Create chunks
    # --------------------------------------------------------

    chunks = chunk_by_title(
        elements,
        max_characters=1000,
        new_after_n_chars=800,
        combine_text_under_n_chars=200
    )

    texts = [
        chunk.text
        for chunk in chunks
        if chunk.text
    ]

    print(
        "Total chunks:",
        len(texts)
    )

    if not texts:

        raise ValueError(
            "No readable text was found in the document."
        )

    # --------------------------------------------------------
    # Load embedding model ONLY when needed
    # --------------------------------------------------------

    embedding_model = get_embedding_model()

    # --------------------------------------------------------
    # Create embeddings
    # --------------------------------------------------------

    embeddings = embedding_model.encode(
        texts
    )

    embeddings = np.array(
        embeddings
    ).astype("float32")

    print(
        "Embedding shape:",
        embeddings.shape
    )

    # --------------------------------------------------------
    # Create FAISS index
    # --------------------------------------------------------

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(
        dimension
    )

    index.add(
        embeddings
    )

    print(
        "Vectors in FAISS:",
        index.ntotal
    )

    # --------------------------------------------------------
    # Reset conversation
    # --------------------------------------------------------

    chat_history = []

    return {
        "chunks": len(texts),
        "vectors": index.ntotal
    }


# ============================================================
# 5. ANSWER QUESTION
# ============================================================

def answer_question(query):

    if index is None or not texts:

        return {
            "answer": "Please upload a document before asking a question.",
            "sources": []
        }

    # --------------------------------------------------------
    # Get embedding model
    # --------------------------------------------------------

    embedding_model = get_embedding_model()

    # ========================================================
    # CREATE HISTORY TEXT
    # ========================================================

    history = ""

    for user_message, assistant_message in chat_history:

        history += f"""
User: {user_message}
Assistant: {assistant_message}
"""

    # ========================================================
    # QUERY REWRITING
    # ========================================================

    rewrite_prompt = f"""
You are a query rewriting assistant for a RAG system.

Your job is to rewrite the user's current question into a
complete, standalone search query.

Use the previous conversation to understand what the user
is referring to.

Previous conversation:
{history}

Current user question:
{query}

Rules:
- If the current question already makes sense by itself,
  keep its meaning.
- If it refers to something from the previous conversation,
  include that topic explicitly.
- Do not answer the question.
- Return ONLY the rewritten search query.

Rewritten search query:
"""

    rewrite_response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=rewrite_prompt
    )

    search_query = (
        rewrite_response.text
        .strip()
    )

    print(
        "\nSearch query:",
        search_query
    )

    # ========================================================
    # EMBED SEARCH QUERY
    # ========================================================

    query_embedding = embedding_model.encode(
        [search_query]
    )

    query_embedding = np.array(
        query_embedding
    ).astype("float32")

    # ========================================================
    # FAISS SEARCH
    # ========================================================

    distances, indices = index.search(
        query_embedding,
        min(3, index.ntotal)
    )

    # ========================================================
    # RETRIEVE CHUNKS
    # ========================================================

    retrieved_chunks = []

    for idx in indices[0]:

        if idx >= 0:

            retrieved_chunks.append(
                texts[idx]
            )

    context = "\n\n".join(
        retrieved_chunks
    )

    # ========================================================
    # FINAL PROMPT
    # ========================================================

    final_prompt = f"""
You are a helpful assistant answering questions about the
provided document.

Use the retrieved context and conversation history to answer
the user's question.

IMPORTANT RULES:

1. Answer using the retrieved context.
2. Use conversation history to understand follow-up questions.
3. Do not make up information.
4. If the answer is not available in the document, say:
   "The information is not available in the document."
5. Give a clear and concise answer.
6. If the user asks for an example, give an example from
   the retrieved context whenever possible.

Previous conversation:
{history}

Retrieved context:
{context}

Current user question:
{query}

Answer:
"""

    # ========================================================
    # GEMINI FINAL ANSWER
    # ========================================================

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=final_prompt
    )

    answer = response.text.strip()

    # ========================================================
    # SAVE CONVERSATION
    # ========================================================

    chat_history.append(
        (query, answer)
    )

    # ========================================================
    # RETURN ANSWER + SOURCES
    # ========================================================

    return {
        "answer": answer,

        "sources": [
            {
                "chunk": int(idx) + 1,
                "text": texts[idx]
            }
            for idx in indices[0]
            if idx >= 0
        ]
    }