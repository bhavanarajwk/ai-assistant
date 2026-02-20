from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

LOG_PATH = "logs/app.log"
PERSIST_DIR = "data/vectorstore"


def chunk_logs_by_lines(log_text, lines_per_chunk=15):
    lines = log_text.split("\n")
    chunks = []

    for i in range(0, len(lines), lines_per_chunk):
        chunk = "\n".join(lines[i:i+lines_per_chunk])
        if chunk.strip():
            chunks.append(chunk)

    return chunks


def ingest_logs():
    print("Loading logs...")

    with open(LOG_PATH, "r") as f:
        log_text = f.read()

    print("Chunking logs by lines...")

    chunks = chunk_logs_by_lines(log_text, lines_per_chunk=15)

    docs = [Document(page_content=chunk) for chunk in chunks]

    print(f"Total chunks created: {len(docs)}")

    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    print("Storing in Chroma...")

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )

    print("✅ Ingestion complete.")


if __name__ == "__main__":
    ingest_logs()