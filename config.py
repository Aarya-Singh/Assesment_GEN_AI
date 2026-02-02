import os
import logging
from dotenv import load_dotenv

# Load environment
load_dotenv()

# --- APP CONFIG ---
APP_NAME = "TechGear Assistant"
DEBUG = True

# --- PATHS ---
CHROMA_DB_PATH = "/home/labuser/Desktop/assesment/chroma_db"
CHROMA_CACHE_PATH = "/home/labuser/Desktop/assesment/chroma_cache"
SESSION_DB_PATH = "/home/labuser/Desktop/assesment/history.db"

# --- RAG SETTINGS ---
COLLECTION_NAME = "customer_support"
CACHE_COLLECTION_NAME = "semantic_cache"
EMBEDDING_MODEL = "models/embedding-001"
GENERATIVE_MODEL = "gemini-2.0-flash"
RETRIEVAL_K = 25
TEMPERATURE = 0.2

# --- CACHE SETTINGS ---
CACHE_THRESHOLD = 0.95

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(APP_NAME)
