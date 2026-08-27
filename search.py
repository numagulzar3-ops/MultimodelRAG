import chromadb
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. Load embedding model
# --------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------------------------
# 2. Connect to ChromaDB
# --------------------------------------------------

client = chromadb.PersistentClient(path="./chroma_db")


# --------------------------------------------------
# 3. Get collection
# --------------------------------------------------

collection = client.get_collection(
    name="java_fundamentals"
)


# --------------------------------------------------
# 4. User query
# --------------------------------------------------

query = "What are wrapper classes in Java?"


# --------------------------------------------------
# 5. Convert query into embedding
# --------------------------------------------------

query_embedding = model.encode(query).tolist()


# --------------------------------------------------
# 6. Search ChromaDB
# --------------------------------------------------

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
    include=["documents", "distances"]
)


# --------------------------------------------------
# 7. Display results
# --------------------------------------------------

print("\n" + "=" * 70)
print("QUERY:")
print(query)

print("\nTOP 3 RELEVANT CHUNKS")
print("=" * 70)


for i, document in enumerate(results["documents"][0]):

    print("\nChunk:", results["ids"][0][i])

    print("Distance:", results["distances"][0][i])

    print("-" * 70)

    print(document)