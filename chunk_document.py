from unstructured.partition.docx import partition_docx

file_path = "data/JAVA FUNDAMENTALS.docx"

elements = partition_docx(filename=file_path)

chunks = []
current_chunk = ""

for element in elements:

    text = element.text.strip()

    if not text:
        continue

    current_chunk += text + "\n"

    if len(current_chunk) >= 500:
        chunks.append(current_chunk)
        current_chunk = ""

if current_chunk:
    chunks.append(current_chunk)

print("Total chunks:", len(chunks))

for i, chunk in enumerate(chunks):
    print("\n" + "=" * 60)
    print("CHUNK", i + 1)
    print("=" * 60)
    print(chunk)