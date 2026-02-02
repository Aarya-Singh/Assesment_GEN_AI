from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import os
from typing import List, Optional

# Import refactored components
from langgraph_workflow import process_query
from config import logger, APP_NAME

app = FastAPI(title=APP_NAME)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    """Refined request model."""
    query: str
    thread_id: str = "default"
    history: List[dict] = []

class QueryResponse(BaseModel):
    """Refined response model."""
    category: str
    response: str

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    try:
        logger.info(f"Received query: {request.query} (Thread: {request.thread_id})")
        
        # Process through pre-compiled LangGraph workflow
        result = process_query(
            query=request.query, 
            thread_id=request.thread_id, 
            history=request.history
        )
        
        return QueryResponse(
            category=result["category"],
            response=result["response"]
        )
    except Exception as e:
        logger.error(f"Error in /chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Senior-grade TechGear Chatbot API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
