import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from config import CHROMA_CACHE_PATH, EMBEDDING_MODEL, CACHE_THRESHOLD, CACHE_COLLECTION_NAME, logger

class CacheManager:
    """Singleton for semantic caching."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        logger.info("Initializing Cache Manager...")
        self.embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        self.cache_db = Chroma(
            persist_directory=CHROMA_CACHE_PATH,
            embedding_function=self.embeddings,
            collection_name=CACHE_COLLECTION_NAME
        )
        logger.info("Cache Manager ready.")

    def get_cached_response(self, query: str):
        """Search for a similar query in the cache."""
        results = self.cache_db.similarity_search_with_relevance_scores(query, k=1)
        
        if results and results[0][1] >= CACHE_THRESHOLD:
            logger.info(f"Cache HIT (similarity: {results[0][1]:.4f})")
            return results[0][0].metadata.get("response")
        
        return None

    def store_in_cache(self, query: str, response: str):
        """Store a query-response pair in the cache."""
        self.cache_db.add_texts(
            texts=[query],
            metadatas=[{"response": response}]
        )
        logger.info("Query stored in semantic cache.")

# Global instance
_cache_instance = None

def get_cached_response(query: str):
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance.get_cached_response(query)

def store_in_cache(query: str, response: str):
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance.store_in_cache(query, response)
