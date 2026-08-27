from sentence_transformers import SentenceTransformer
from unstructured.partition.docx import partition_docx
from unstructured.chunking.title import chunk_by_title
from sklearn.metrics.pairwise import cosine_similarity


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
# 3. Load embedding model
# --------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------------------------
# 4. Extract text from chunks
# --------------------------------------------------

texts = [chunk.text for chunk in chunks]


# --------------------------------------------------
# 5. Create embeddings for all chunks
# --------------------------------------------------

embeddings = model.encode(texts)

print("Number of embeddings:", len(embeddings))
print("Dimensions of each embedding:", len(embeddings[0]))


# --------------------------------------------------
# 6. User's question
# --------------------------------------------------

query = "What are wrapper classes in Java?"


# --------------------------------------------------
# 7. Convert question into an embedding
# --------------------------------------------------

query_embedding = model.encode([query])


# --------------------------------------------------
# 8. Calculate similarity
# --------------------------------------------------

similarities = cosine_similarity(
    query_embedding,
    embeddings
)[0]


# --------------------------------------------------
# 9. Get the top 3 most similar chunks
# --------------------------------------------------

top_indices = similarities.argsort()[-3:][::-1]


# --------------------------------------------------
# 10. Display results
# --------------------------------------------------

print("\n" + "=" * 70)
print("QUERY:")
print(query)

print("\nTOP 3 RELEVANT CHUNKS")
print("=" * 70)

for index in top_indices:

    print("\nChunk:", index + 1)
    print("Similarity:", similarities[index])
    print("-" * 70)
    print(texts[index])