from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

PERSIST_DIR = "data/vectorstore"

def get_retriever():
    # Initialize embedding model
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    # Load existing Chroma DB
    vectorstore = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )

    # Create retriever
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}  # return top 3 relevant chunks
    )

    return retriever
