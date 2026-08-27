from sentence_transformers import SentenceTransformer
from unstructured.partition.docx import partition_docx
from unstructured.chunking.title import chunk_by_title
import faiss
import numpy as np
import ollama


# ============================================================
# 1. LOAD DOCUMENT
# ============================================================

file_path = "data/JAVA FUNDAMENTALS.docx"

elements = partition_docx(filename=file_path)


# ============================================================
# 2. CREATE CHUNKS
# ============================================================

chunks = chunk_by_title(
    elements,
    max_characters=1000,
    new_after_n_chars=800,
    combine_text_under_n_chars=200
)

texts = [chunk.text for chunk in chunks]

print("Total chunks:", len(chunks))


# ============================================================
# 3. LOAD EMBEDDING MODEL
# ============================================================

model = SentenceTransformer("all-MiniLM-L6-v2")


# ============================================================
# 4. CREATE EMBEDDINGS
# ============================================================

embeddings = model.encode(texts)

embeddings = np.array(embeddings).astype("float32")

print("Embedding shape:", embeddings.shape)


# ============================================================
# 5. CREATE FAISS VECTOR STORE
# ============================================================

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

print("Vectors in FAISS:", index.ntotal)


# ============================================================
# 6. CONVERSATION MEMORY
# ============================================================

chat_history = []


# ============================================================
# 7. CHAT LOOP
# ============================================================

while True:

    query = input("\nYou: ")

    if query.lower() == "exit":
        print("Goodbye!")
        break


    # ========================================================
    # 8. CREATE HISTORY TEXT
    # ========================================================

    history = ""

    for user_message, assistant_message in chat_history:

        history += f"""
User: {user_message}
Assistant: {assistant_message}
"""


    # ========================================================
    # 9. REWRITE QUERY USING CONVERSATION HISTORY
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


    rewrite_response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": rewrite_prompt
            }
        ]
    )


    search_query = rewrite_response["message"]["content"].strip()


    # ========================================================
    # 10. SHOW REWRITTEN QUERY
    # ========================================================

    print("\nSearch query:", search_query)


    # ========================================================
    # 11. EMBED REWRITTEN QUERY
    # ========================================================

    query_embedding = model.encode([search_query])

    query_embedding = np.array(query_embedding).astype("float32")


    # ========================================================
    # 12. SEARCH FAISS
    # ========================================================

    distances, indices = index.search(
        query_embedding,
        3
    )


    # ========================================================
    # 13. RETRIEVE RELEVANT CHUNKS
    # ========================================================

    retrieved_chunks = []

    for idx in indices[0]:

        retrieved_chunks.append(texts[idx])


    context = "\n\n".join(retrieved_chunks)


    # ========================================================
    # 14. SHOW RETRIEVED CHUNKS
    # ========================================================

    print("\nRetrieved chunks:")

    for i, idx in enumerate(indices[0]):

        print("\nChunk:", idx + 1)
        print("Distance:", distances[0][i])
        print("-" * 60)


    # ========================================================
    # 15. CREATE FINAL PROMPT
    # ========================================================

    final_prompt = f"""
You are a helpful assistant answering questions about the
provided Java document.

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
    # 16. SEND TO LLAMA
    # ========================================================

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": final_prompt
            }
        ]
    )


    # ========================================================
    # 17. GET ANSWER
    # ========================================================

    answer = response["message"]["content"]


    # ========================================================
    # 18. SAVE CONVERSATION
    # ========================================================

    chat_history.append(
        (query, answer)
    )


    # ========================================================
    # 19. DISPLAY ANSWER
    # ========================================================

    print("\n" + "=" * 70)
    print("AI ANSWER")
    print("=" * 70)

    print(answer)