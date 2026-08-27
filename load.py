from unstructured.partition.docx import partition_docx

file_path = "data/JAVA FUNDAMENTALS.docx"

elements = partition_docx(filename=file_path)

for element in elements:
    print("TYPE:", type(element).__name__)
    print("TEXT:", element.text)
    print("-" * 50)