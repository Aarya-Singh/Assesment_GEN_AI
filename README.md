# TechGear AI Support Assistant 🤖

A high-performance, context-aware RAG chatbot for customer support and consultative sales.

## Features
- **Semantic Search**: Powered by ChromaDB and Google Gemini.
- **Consultative Sales Agent**: Recommends products based on budget and features.
- **Multi-language Support**: Automatically detects and responds in the user's language.
- **Smart Memory**: Persistent conversation history via SQLite.
- **Semantic Caching**: Ultra-fast responses for repeated queries.
- **Premium UI**: Modern glassmorphism design with markdown support.

## Tech Stack
- **Backend**: Python, FastAPI, LangChain, LangGraph.
- **Frontend**: Vanilla JS, CSS (Modern UI), Marked.js.
- **Models**: Google Gemini 2.0 Flash, Embedding-001.

## Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Configure your `.env` file with `GOOGLE_API_KEY`.
4. Run the data ingestion: `python setup_vectordb.py`. (Add more data to `prodcut_info.txt` if needed).
5. Start the server: `python main.py`.

## Senior Engineering Highlights
- **Singleton Pattern**: AI models and DB connections are shared across sessions for efficiency.
- **Pre-compiled Graph**: LangGraph is compiled at startup to minimize latency.
- **Structured Logging**: Centralized logging in `app.log`.
- **Clean Configuration**: All settings managed in `config.py`.
