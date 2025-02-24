from docling.document_converter import DocumentConverter

converter = DocumentConverter()

#HTML extraction
result = converter.convert("https://learnconline.com")
document = result.document
markdown_output = document.export_to_markdown()
json_output = document.export_to_dict()
print(json_output)