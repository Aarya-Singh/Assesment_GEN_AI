import os
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from rag_chain import get_rag_response
from semantic_cache import get_cached_response, store_in_cache
from config import GENERATIVE_MODEL, TEMPERATURE, SESSION_DB_PATH, logger

class WorkflowState(TypedDict):
    """Conversation state."""
    query: str
    category: str
    language: str
    response: str
    history: list

# --- Shared LLM for nodes ---
_node_llm = None
def get_llm():
    global _node_llm
    if _node_llm is None:
        _node_llm = ChatGoogleGenerativeAI(model=GENERATIVE_MODEL, temperature=TEMPERATURE)
    return _node_llm

def classify_node(state: WorkflowState) -> WorkflowState:
    """Detect language and intent."""
    llm = get_llm()
    history_context = "\n".join([f"{m['role']}: {m['content']}" for m in state.get("history", [])[-2:]])
    
    prompt = f"""Conversation History:
    {history_context}
    
    Current Query: {state['query']}
    
    Perform two tasks:
    1. Language Detection: Identify the language of the 'Current Query'.
    2. Category Classification: Classify into 'greeting', 'products', 'returns', or 'general'.
    
    Return exactly in this format:
    LANGUAGE: [Detected Language]
    CATEGORY: [greeting/products/returns/general]"""
    
    output = llm.invoke(prompt).content.strip()
    logger.info(f"Classification Output: {output}")
    
    try:
        lines = output.split("\n")
        language = lines[0].split(":")[1].strip()
        category = lines[1].split(":")[1].strip().lower()
    except Exception as e:
        logger.error(f"Classification parse error: {e}")
        language = "English"
        category = "general"

    state["category"] = category if category in ["greeting", "products", "returns", "general"] else "general"
    state["language"] = language
    return state

def greeting_node(state: WorkflowState) -> WorkflowState:
    """Respond with greeting in detected language with chatbot tone."""
    llm = get_llm()
    prompt = f"""The user said '{state['query']}'. Language: {state['language']}. 
    Introduce yourself as the TechGear AI Assistant in {state['language']}. 
    Greet them warmly and mention you can help with products and returns.
    
    IMPORTANT: Respond ONLY with a conversational message. Do NOT use subjects, headers, or formal letter formats."""
    state["response"] = llm.invoke(prompt).content
    return state

def rag_responder_node(state: WorkflowState) -> WorkflowState:
    """Answer via Cache or RAG."""
    query = state["query"]
    recent_history = " ".join([m['content'] for m in state.get("history", [])[-2:]])
    contextual_query = f"{recent_history} {query}".strip()

    # 1. Cache Check
    cached = get_cached_response(contextual_query)
    if cached:
        state["response"] = cached
        return state

    # 2. RAG Generation
    response = get_rag_response({"question": contextual_query, "language": state["language"]})
    
    # 3. Cache Store
    store_in_cache(contextual_query, response)
    
    state["response"] = response
    return state

def escalation_node(state: WorkflowState) -> WorkflowState:
    """Escalate in user language with a conversational chatbot tone."""
    llm = get_llm()
    prompt = f"""The user query is '{state['query']}'. Language: {state['language']}. 
    Respond as the TechGear AI Assistant. Politely explain that you are an AI and cannot connect them to a live human directly in this chat.
    Provide our support email (support@techgear.com) for human assistance.
    
    IMPORTANT: Respond ONLY with the conversational message in {state['language']}. Do NOT include subjects, headers, signatures, or email-style formatting."""
    state["response"] = llm.invoke(prompt).content
    return state

def route_query(state: WorkflowState) -> Literal["greeting_node", "rag_responder", "escalation"]:
    if state["category"] == "greeting": return "greeting_node"
    if state["category"] in ["products", "returns"]: return "rag_responder"
    return "escalation"

class WorkflowManager:
    """Singleton for LangGraph execution."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WorkflowManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        logger.info("Initializing Workflow Manager...")
        # For SqliteSaver, we need to manage the connection. 
        # Using a simple singleton instance if possible.
        self.saver = SqliteSaver.from_conn_string(SESSION_DB_PATH)
        
        workflow = StateGraph(WorkflowState)
        workflow.add_node("classifier", classify_node)
        workflow.add_node("greeting_node", greeting_node)
        workflow.add_node("rag_responder", rag_responder_node)
        workflow.add_node("escalation", escalation_node)
        
        workflow.set_entry_point("classifier")
        workflow.add_conditional_edges("classifier", route_query, {
            "greeting_node": "greeting_node",
            "rag_responder": "rag_responder",
            "escalation": "escalation"
        })
        workflow.add_edge("greeting_node", END)
        workflow.add_edge("rag_responder", END)
        workflow.add_edge("escalation", END)
        
        # We enter the context manager once and keep it open for the singleton
        self._conn = self.saver.__enter__()
        self.app = workflow.compile(checkpointer=self._conn)
        logger.info("Workflow Graph compiled with SqliteSaver.")

_workflow_instance = None

def process_query(query: str, thread_id: str = "default", history: list = []):
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = WorkflowManager()
        
    config = {"configurable": {"thread_id": thread_id}}
    result = _workflow_instance.app.invoke({"query": query, "history": history}, config)
    return {"category": result["category"], "response": result["response"]}
