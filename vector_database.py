import chromadb
from sentence_transformers import SentenceTransformer
from unstructured.partition.docx import partition_docx
from unstructured.chunking.title import chunk_by_title


# --------------------------------------------------
# 1. Load the document
# --------------------------------------------------

file_path = "data/JAVA FUNDAMENTALS.docx"

elements = partition_docx(filename=file_path)


# --------------------------------------------------
# 2. Create chunks
# --------------------------------------------------

chunks = chunk_by_title(
    elements,
    max_characters=1000,
    new_after_n_chars=800,
    combine_text_under_n_chars=200
)

print("Total chunks:", len(chunks))


# --------------------------------------------------
# 3. Extract text
# --------------------------------------------------

texts = [chunk.text for chunk in chunks]


# --------------------------------------------------
# 4. Load embedding model
# --------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------------------------
# 5. Create embeddings
# --------------------------------------------------

embeddings = model.encode(texts)

print("Number of embeddings:", len(embeddings))
print("Embedding dimensions:", len(embeddings[0]))


# --------------------------------------------------
# 6. Create ChromaDB client
# --------------------------------------------------

client = chromadb.PersistentClient(path="./chroma_db")


# --------------------------------------------------
# 7. Create collection
# --------------------------------------------------

collection = client.get_or_create_collection(
    name="java_fundamentals"
)


# --------------------------------------------------
# 8. Store chunks + embeddings
# --------------------------------------------------

collection.add(
    ids=[f"chunk_{i}" for i in range(len(texts))],
    documents=texts,
    embeddings=embeddings.tolist()
)


# --------------------------------------------------
# 9. Check database
# --------------------------------------------------

print("Documents stored in ChromaDB:", collection.count())