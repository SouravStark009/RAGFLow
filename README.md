# RAGFlow

A durable, event-driven Retrieval-Augmented Generation (RAG) pipeline for PDF documents — built with **FastAPI**, **Inngest**, **Qdrant**, and **Google Gemini**.

Upload a PDF, it gets chunked and embedded into a vector store. Ask a question, and Gemini answers using only the retrieved context — no hallucinated answers outside your documents.

## How It Works

1. **Ingest** — A PDF is loaded, split into overlapping text chunks, embedded via Gemini's embedding model, and upserted into Qdrant.
2. **Query** — A question is embedded, the most relevant chunks are retrieved from Qdrant, and Gemini generates an answer grounded in that context.

Each step runs as a durable, retryable **Inngest function**, so long-running or failure-prone steps (PDF parsing, embedding calls, LLM generation) can recover from partial failures instead of restarting the whole pipeline.

## Tech Stack

| Component | Tool |
|---|---|
| API framework | FastAPI |
| Workflow orchestration | Inngest |
| Vector database | Qdrant |
| Embeddings | Gemini `gemini-embedding-001` (3072-dim) |
| LLM | Gemini `gemini-2.5-flash` |
| PDF parsing / chunking | LlamaIndex (`PDFReader`, `SentenceSplitter`) |

## Project Structure

```
.
├── main.py           # FastAPI app + Inngest function definitions
├── data_loader.py     # PDF loading, chunking, and embedding
├── vector_db.py        # Qdrant storage wrapper (upsert / search)
├── custom_types.py       # Pydantic models for step inputs/outputs
└── README.md
```

## Setup

### Prerequisites

- Python 3.10+
- A running [Qdrant](https://qdrant.tech/) instance (default: `http://localhost:6333`)
- Google Gemini API key
- [Inngest CLI](https://www.inngest.com/docs/dev-server) (for local development)

### Installation

```bash
git clone https://github.com/SouravStark009/RAGFLow.git
cd RAGFLow
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Running Locally

**1. Start Qdrant** (via Docker):
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**2. Start the FastAPI app:**
```bash
uvicorn main:app --reload --port 8000
```

**3. Start the Inngest Dev Server** (in a separate terminal):
```bash
npx inngest-cli@latest dev
```

The Dev Server will auto-discover your app at `http://localhost:8000/api/inngest`.

## Usage

### Ingest a PDF

Send an `rag/ingest_pdf` event with a `pdf_path`:

```json
{
  "name": "rag/ingest_pdf",
  "data": {
    "pdf_path": "/path/to/document.pdf",
    "source_id": "document.pdf"
  }
}
```

### Ask a Question

Send an `rag/query_pdf_ai` event:

```json
{
  "name": "rag/query_pdf_ai",
  "data": {
    "question": "How much is the amount paid?",
    "top_k": 5
  }
}
```

Response:

```json
{
  "answer": "...",
  "sources": ["document.pdf"],
  "num_contexts": 3
}
```

## License

MIT — see [LICENSE](./LICENSE).