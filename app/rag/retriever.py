from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

PERSIST_DIR = "data/vectorstore"

def get_retriever():
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    vectorstore = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )

    return retriever
