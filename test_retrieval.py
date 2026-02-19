import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath("."))

from app.rag.retriever import get_retriever

retriever = get_retriever()

query = "500 error after deployment"

docs = retriever.invoke(query)


print("Number of retrieved docs:", len(docs))

for i, doc in enumerate(docs):
    print(f"\n--- Chunk {i+1} ---")
    print(doc.page_content)
