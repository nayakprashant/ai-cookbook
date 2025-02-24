from docling.document_converter import DocumentConverter

converter = DocumentConverter()

#PDF extraction
result = converter.convert("https://arxiv.org/pdf/2408.09869")
document = result.document
markdown_output = document.export_to_markdown()
json_output = document.export_to_dict()
print(json_output)