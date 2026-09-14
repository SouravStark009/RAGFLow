import logging
from pathlib import Path
from google import genai
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("uvicorn")

client = genai.Client()

EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 3072

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

def load_and_chunk_pdf(path: str):
    docs = PDFReader().load_data(file=Path(path))
    logger.info(f"PDFReader loaded {len(docs)} doc(s) from {path}")

    texts = [d.text for d in docs if getattr(d, "text", None)]
    logger.info(f"Extracted {len(texts)} non-empty text block(s)")

    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    logger.info(f"Total chunks after splitting: {len(chunks)}")

    return chunks

def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        raise ValueError("embed_texts received an empty list — no chunks to embed!")

    logger.info(f"Embedding {len(texts)} chunk(s)...")
    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=texts,
        config={"output_dimensionality": EMBED_DIM}
    )
    logger.info(f"Received {len(response.embeddings)} embedding(s) back")
    return [item.values for item in response.embeddings]