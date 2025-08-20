import os
import chromadb
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

KNOWLEDGE_BASE_DIR  = "knowledge_base"
CHROMA_PERSIST_DIR =  "chroma_db"

print("starting database seeding")

print("Loading docs from {KNOWLEDGE_BASE_DIR}")

#make an object of DirectoryLoader class

loader = DirectoryLoader(
    KNOWLEDGE_BASE_DIR,
    glob="**/*.txt",#glob — Unix style pathname pattern expansion 
    loader_cls=TextLoader,
    loader_kwargs={'encoding':'utf-8'},
    show_progress=True
)

# loader itself is like a “manager” that:
# Knows where to search (KNOWLEDGE_BASE_DIR).
# Knows what to include (glob="**/*.txt").
# Knows how to read each file (loader_cls=TextLoader).
# Knows extra settings for reading (loader_kwargs).

documents = loader.load()#returns a list, documents is a list
print(f"loaded {len(documents)} documents")

# -----------split documents into chunks----------------

text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap=200)
# RecursiveCharacterTextSplitter tries to break text intelligently: It first tries splitting by paragraphs (\n\n).
# If the chunk is still too big, it tries sentences. Then words.nFinally, if needed, by characters.
docs = text_splitter.split_documents(documents)

# Input: a list of LangChain Document objects.
# Output: a list of new Document objects, each chunk is a document, and metadata is preserved.
# in case of .split_text(text) input is a single string and outpur is list of strings
# docs = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap=200).split_documents(documents)

print(f"split documents into {len(docs)} chunks")

print("----------Now Initializing Embedding model-----------------")

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
# SentenceTransformerEmbeddings = a LangChain wrapper around HuggingFace’s SentenceTransformers library.

print(f"creating chromaDB at {CHROMA_PERSIST_DIR}")
# -------------------------crearing chroma db----------------------

db= Chroma.from_documents(
    docs, 
    embedding_function,
    persist_directory=CHROMA_PERSIST_DIR
)
# db is your LangChain Chroma vectorstore object.
#.from_documents is a class method to create a chroma db directly from your documents

print("Database made")
print(f"Total chunks processed  {len(docs)}")
print(f"chromaDB collection count: {db._collection.count()}")
