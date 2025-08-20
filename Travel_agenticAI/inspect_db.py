from langchain_chroma import Chroma

CHROMA_PERSIST_DIR = "chroma_db"

# Load DB without embedding function (ok for inspection)
db = Chroma(persist_directory=CHROMA_PERSIST_DIR)

# Raw collection
collection = db._collection

# Basic info
print("Total embeddings stored:", collection.count())

# # Fetch first 2 entries (ids, documents, metadata only)
# res = collection.get(limit=2, include=["documents", "metadatas"])
# print("\nSample documents:")
# for doc in res["documents"]:
#     print("-", doc[:150])  # show first 150 characters

res = collection.get(limit=1, include=["documents", "embeddings"])
print("First document text:", res["documents"][0][:200])
print("First embedding vector length:", len(res["embeddings"][0])) #should be 384 as all-MiniLM-L6-v2 produces 384-dimensional vectors
print("First 10 values:", res["embeddings"][0][:10])
