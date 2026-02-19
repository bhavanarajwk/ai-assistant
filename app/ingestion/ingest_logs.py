import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# Paths
LOG_PATH = "logs/app.log"
PERSIST_DIR = "data/vectorstore"

def ingest_logs():
    print("Loading logs...")

    # Load log file
    loader = TextLoader(LOG_PATH)
    documents = loader.load()

    print("Splitting logs into chunks...")

    # Split logs into chunks
    text_splitter = CharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    docs = text_splitter.split_documents(documents)

    print(f"Total chunks created: {len(docs)}")

    print("Creating embeddings using Ollama...")

    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    print("Storing in Chroma vector DB...")

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )

    vectorstore.persist()

    print("✅ Logs successfully ingested and stored!")

if __name__ == "__main__":
    ingest_logs()
