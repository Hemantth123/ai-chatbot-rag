from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
import numexpr
import re

def calculator(expression: str) -> str:
    """Calculate mathematical expressions using numexpr."""
    try:
        result = numexpr.evaluate(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

def load_rag():
    try:
        loader = TextLoader("data/sample.txt", encoding="utf-8")
        docs = loader.load()

        splitter = CharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=10,
            separator="\n"
        )

        texts = splitter.split_documents(docs)

        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        db = FAISS.from_documents(texts, embeddings)

        llm = ChatOllama(model="gemma:2b")
        return {"db": db, "llm": llm, "available": True}
    except Exception as e:
        print(f"Ollama not available: {e}")
        return {"available": False}

def agent_respond(question, rag):
    """Simple agent that decides whether to use RAG or calculator."""
    if not rag.get("available", False):
        # Fallback responses
        if "calculate" in question.lower() or "math" in question.lower():
            return calculator(question)
        elif "hello" in question.lower() or "hi" in question.lower():
            return "Hello! I'm your AI assistant. Ollama is not configured, so I can only do basic calculations."
        else:
            return "I'm running in limited mode. I can help with calculations, but for other questions, please set up Ollama."
    
    # Check if the question contains mathematical expressions
    math_patterns = [
        r'\d+\s*[\+\-\*\/]\s*\d+',  # basic arithmetic
        r'calculate', r'compute', r'math', r'what is', r'solve'
    ]
    
    if any(re.search(pattern, question.lower()) for pattern in math_patterns):
        # Try to extract mathematical expression
        expr_match = re.search(r'(\d+(?:\.\d+)?\s*[\+\-\*\/]\s*\d+(?:\.\d+)?)', question)
        if expr_match:
            return calculator(expr_match.group(1))
        else:
            return "I can help with calculations. Please provide a mathematical expression."
    
    # Otherwise, use RAG
    docs = rag["db"].similarity_search(question, k=1)
    if not docs:
        return "No relevant information found in documents."

    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
Use the context below to answer the question.
If the context doesn't help, say you don't know.

Context:
{context}

Question: {question}

Answer:"""

    response = rag["llm"].invoke(prompt)
    return response.content