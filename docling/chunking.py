from docling.document_converter import DocumentConverter
from transformers import AutoTokenizer
from docling.chunking import HybridChunker

converter = DocumentConverter()

#PDF extraction
result = converter.convert("https://arxiv.org/pdf/2408.09869")
document = result.document

#Basic chunking
chunker = HybridChunker()
chunk_iter = chunker.chunk(dl_doc=document)

for i, chunk in enumerate(chunk_iter):
    print(f"=== {i} ===")
    print(f"chunk.text:\n{repr(f'{chunk.text[:300]}…')}")

    #Note that the text you would typically want to embed is the context-enriched one as returned by the serialize() method:
    enriched_text = chunker.serialize(chunk=chunk)
    print(f"chunker.serialize(chunk):\n{repr(f'{enriched_text[:300]}…')}")

#Hybrid chunking
EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MAX_TOKENS = 1000  # set to a small number for illustrative purposes

tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL_ID)

chunker = HybridChunker(
    tokenizer=tokenizer,  # instance or model name, defaults to "sentence-transformers/all-MiniLM-L6-v2"
    max_tokens=MAX_TOKENS,  # optional, by default derived from `tokenizer`
    merge_peers=True,  # optional, defaults to True
)

chunk_iter = chunker.chunk(dl_doc=document)
chunks = list(chunk_iter)

for i, chunk in enumerate(chunks):
    print(f"=== {i} ===")
    txt_tokens = len(tokenizer.tokenize(chunk.text, max_length=None))
    print(f"chunk.text ({txt_tokens} tokens):\n{repr(chunk.text)}")

    ser_txt = chunker.serialize(chunk=chunk)
    ser_tokens = len(tokenizer.tokenize(ser_txt, max_length=None))
    print(f"chunker.serialize(chunk) ({ser_tokens} tokens):\n{repr(ser_txt)}")