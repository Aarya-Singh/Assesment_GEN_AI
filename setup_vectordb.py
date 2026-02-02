"""
Task 1: Setup & Document Loading
This script handles loading the knowledge base, splitting into chunks,
creating embeddings, and storing in ChromaDB.
"""

import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma


def setup_vector_database():
    """
    Load knowledge base, create embeddings, and store in ChromaDB.
    """
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    # Load the knowledge base
    print("Loading knowledge base...")
    with open("prodcut_info.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
    
    # Split text into chunks using RecursiveCharacterTextSplitter
    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_text(knowledge_base)
    print(f"Created {len(chunks)} chunks")
    
    # Create embeddings using Google's embedding model
    print("Creating embeddings...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )
    
    # Store in ChromaDB with persistence
    print("Clearing existing collection to avoid duplicates...")
    # Delete the collection if it exists
    if os.path.exists("./chroma_db"):
        import shutil
        # It's cleaner to just delete the directory for a fresh start in this setup
        shutil.rmtree("./chroma_db")
        
    print("Storing in ChromaDB...")
    vectordb = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db",
        collection_name="customer_support"
    )
    
    print("✓ Vector database setup complete!")
    print(f"  - Collection: customer_support")
    print(f"  - Documents: {len(chunks)}")
    print(f"  - Storage: ./chroma_db")
    
    return vectordb


if __name__ == "__main__":
    setup_vector_database()
