import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
from config import (
    CHROMA_DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL, 
    GENERATIVE_MODEL, RETRIEVAL_K, TEMPERATURE, logger
)

class RAGManager:
    """Singleton for managing the RAG pipeline."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        logger.info("Initializing RAG Manager...")
        self.embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        self.vectorstore = Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding_function=self.embeddings,
            collection_name=COLLECTION_NAME
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": RETRIEVAL_K})
        self.llm = ChatGoogleGenerativeAI(model=GENERATIVE_MODEL, temperature=TEMPERATURE)
        
        template = """You are a Consultative Sales Assistant for TechGear. 
        Your goal is to help the user find the best product(s) based on their needs.
        
        IMPORTANT: You MUST respond in the identified language: {language}
        
        GUIDELINES:
        1. FILTERING: If the user provides a budget, list all unique products from the context that fit that price.
        2. BUNDLING: If the user asks for a 'pair' or 'set', browse the context for items in multiple categories, sum their prices, and suggest the best combination within budget.
        3. COMPARISON: Compare features of the items in context and recommend one based on preferences.
        4. MISSING FEATURES: If a feature is missing, politely say so in the user's language and suggest the closest product.
        5. KNOWLEDGE: Use ONLY the provided context. If no product fits, offer technical support.
        6. TONE: Respond in a clean, conversational chatbot format. Do NOT use subjects, email headers (Subject/Body), signatures, or formal letter conventions.
        
        Context: {context}
        
        Question: {question}
        """
        self.prompt = ChatPromptTemplate.from_template(template)
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        self.chain = (
            {
                "context": itemgetter("question") | self.retriever | format_docs, 
                "question": itemgetter("question"),
                "language": itemgetter("language")
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        logger.info("RAG Chain ready.")

    def get_response(self, question: str, language: str = "English"):
        return self.chain.invoke({"question": question, "language": language})

# Global instance
_rag_instance = None

def get_rag_response(input_data):
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGManager()
        
    if isinstance(input_data, str):
        return _rag_instance.get_response(input_data)
    return _rag_instance.get_response(input_data["question"], input_data.get("language", "English"))
