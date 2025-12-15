# chromadb_setup.py
import chromadb
from chromadb.config import Settings
import os

def setup_chromadb():
    # Create directory if it does not exist
    persist_dir = "./chroma_db"
    os.makedirs(persist_dir, exist_ok=True)
    
    # Setup ChromaDB client
    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=persist_dir,
        anonymized_telemetry=False
    ))
    
    # Test the connection
    try:
        collections = client.list_collections()
        print(f"Connected to ChromaDB. Collections: {[c.name for c in collections]}")
        
        # Create default collection if it doesn't exist
        default_collection = client.get_or_create_collection(name="companies")
        print(f"Created/retrieved 'companies' collection")
        
        return client
    except Exception as e:
        print(f"Setup failed: {e}")
        return None

if __name__ == "__main__":
    setup_chromadb()