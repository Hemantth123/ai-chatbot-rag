# AI Chatbot with Agents

An intelligent chatbot built with FastAPI, LangChain, and AI agents that can answer questions from documents and perform calculations.

## Features

- **AI Agents**: The chatbot uses intelligent agents that can decide whether to:
  - Search through uploaded documents (RAG)
  - Perform mathematical calculations
  - Provide fallback responses when AI models aren't available

- **Document Upload**: Upload text files to expand the chatbot's knowledge base
- **User Authentication**: Sign up and login to manage your chat sessions
- **Session Management**: Create multiple chat sessions and export conversations
- **Web Interface**: Clean, responsive web UI for easy interaction

## Setup

### Prerequisites

1. **Python 3.8+**
2. **Ollama** (for full AI capabilities)

### Installation

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama** (optional but recommended for full functionality):
   - Download from https://ollama.ai/
   - Pull required models:
     ```bash
     ollama pull nomic-embed-text
     ollama pull gemma:2b
     ```

### Running the Application

```bash
python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000 in your browser.

## Usage

### Without Ollama
- The chatbot will work in limited mode
- Can perform calculations (e.g., "calculate 2 + 3")
- Basic greetings and responses

### With Ollama
- Full AI capabilities enabled
- Answers questions based on uploaded documents
- Intelligent agent behavior for different types of queries

### Agent Capabilities

The AI agent can:
- **Document Search**: Answer questions using information from uploaded documents
- **Calculations**: Perform mathematical operations like "what is 15 * 7"
- **Smart Routing**: Automatically decide which tool to use based on the question

## API Endpoints

- `GET /` - Home page
- `POST /signup` - User registration
- `POST /login` - User login
- `POST /session/{user_id}` - Create new chat session
- `POST /chat` - Send message to chatbot
- `POST /upload` - Upload document file
- `GET /export/txt/{session_id}` - Export chat as text
- `GET /export/pdf/{session_id}` - Export chat as PDF

## File Structure

```
├── main.py          # FastAPI application
├── rag.py           # RAG and agent logic
├── database.py      # SQLite database operations
├── requirements.txt # Python dependencies
├── templates/
│   └── index.html   # Web interface
├── static/
│   └── style.css    # CSS styles
└── data/
    └── sample.txt   # Sample document data
```

## Customization

- **Models**: Change the Ollama models in `rag.py`
- **UI**: Modify `templates/index.html` and `static/style.css`
- **Agent Behavior**: Enhance the `agent_respond` function in `rag.py`

## License

MIT License