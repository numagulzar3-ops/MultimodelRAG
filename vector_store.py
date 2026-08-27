import faiss
import numpy as np

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

print("Embedding shape:", embeddings.shape)


# --------------------------------------------------
# 6. Convert embeddings to NumPy float32
# --------------------------------------------------

embeddings = np.array(embeddings).astype("float32")


# --------------------------------------------------
# 7. Create FAISS index
# --------------------------------------------------

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)


# --------------------------------------------------
# 8. Add embeddings to FAISS
# --------------------------------------------------

index.add(embeddings)

print("Number of vectors in FAISS:", index.ntotal)


# --------------------------------------------------
# 9. Create query
# --------------------------------------------------

query = "What are wrapper classes in Java?"


# --------------------------------------------------
# 10. Convert query into embedding
# --------------------------------------------------

query_embedding = model.encode([query])

query_embedding = np.array(query_embedding).astype("float32")


# --------------------------------------------------
# 11. Search FAISS
# --------------------------------------------------

k = 3

distances, indices = index.search(query_embedding, k)


# --------------------------------------------------
# 12. Display results
# --------------------------------------------------

print("\n" + "=" * 70)
print("QUERY:")
print(query)

print("\nTOP 3 RELEVANT CHUNKS")
print("=" * 70)

for i in range(k):

    chunk_index = indices[0][i]

    print("\nChunk:", chunk_index + 1)
    print("Distance:", distances[0][i])
    print("-" * 70)

    print(texts[chunk_index])