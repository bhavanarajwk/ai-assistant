from app.rag.retriever import get_retriever

retriever = get_retriever()

query = "Why did 500 errors increase after deployment?"

docs = retriever.get_relevant_documents(query)

print("Retrieved Documents:\n")

for i, doc in enumerate(docs):
    print(f"--- Chunk {i+1} ---")
    print(doc.page_content)
    print("\n")
