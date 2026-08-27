from unstructured.partition.docx import partition_docx
from unstructured.chunking.title import chunk_by_title

file_path = "data/JAVA FUNDAMENTALS.docx"

elements = partition_docx(filename=file_path)

chunks = chunk_by_title(
    elements,
    max_characters=1000,
    new_after_n_chars=800,
    combine_text_under_n_chars=200
)

print("Total chunks:", len(chunks))

for i, chunk in enumerate(chunks):
    print("\n" + "=" * 70)
    print("CHUNK", i + 1)
    print("=" * 70)
    print(chunk.text)