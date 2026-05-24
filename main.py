from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from rag import load_rag, agent_respond
from database import (
    create_user,
    login_user,
    create_session,
    get_sessions,
    save_message,
    get_messages,
    delete_session,
    clear_all,
    get_stats
)
from reportlab.pdfgen import canvas
import os

app = FastAPI(
    title="Hemanth AI",
    description="AI Chatbot by Hemanth",
    version="1.0.0"
)

os.makedirs("data", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

rag = None


# ---------- MODELS ---------- #

class Query(BaseModel):
    question: str
    session_id: int


class UserAuth(BaseModel):
    username: str
    password: str


# ---------- HOME ---------- #

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- ANALYTICS ---------- #

@app.get("/analytics")
def analytics():
    return get_stats()


# ---------- AUTH ---------- #

@app.post("/signup")
def signup(user: UserAuth):
    ok = create_user(user.username, user.password)

    if ok:
        return {"message": "Signup successful"}

    return {"message": "Username already exists"}


@app.post("/login")
def login(user: UserAuth):
    uid = login_user(user.username, user.password)

    if uid:
        return {
            "message": "Login successful",
            "user_id": uid
        }

    return {"message": "Invalid login"}


# ---------- SESSIONS ---------- #

@app.post("/session/{user_id}")
def new_session(user_id: int):
    sid = create_session(user_id)
    return {"session_id": sid}


@app.get("/sessions/{user_id}")
def sessions(user_id: int):
    return {"sessions": get_sessions(user_id)}


@app.get("/history/{session_id}")
def history(session_id: int):
    return {"messages": get_messages(session_id)}


@app.delete("/session/{session_id}")
def remove_session(session_id: int):
    delete_session(session_id)
    return {"message": "Session deleted"}


@app.delete("/clear-all")
def remove_all():
    clear_all()
    return {"message": "All chats deleted"}


# ---------- EXPORT ---------- #

@app.get("/export/txt/{session_id}")
def export_txt(session_id: int):
    messages = get_messages(session_id)
    filename = f"chat_{session_id}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        for role, msg in messages:
            f.write(f"{role.upper()}: {msg}\n\n")

    return FileResponse(
        path=filename,
        filename=filename,
        media_type="text/plain"
    )


@app.get("/export/pdf/{session_id}")
def export_pdf(session_id: int):
    messages = get_messages(session_id)
    filename = f"chat_{session_id}.pdf"

    c = canvas.Canvas(filename)
    y = 800

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Chat Export - Session {session_id}")
    y -= 30

    for role, msg in messages:
        text = f"{role.upper()}: {msg}"
        lines = text.split("\n")

        for line in lines:
            c.drawString(50, y, line[:100])
            y -= 20

            if y < 50:
                c.showPage()
                y = 800

    c.save()

    return FileResponse(
        path=filename,
        filename=filename,
        media_type="application/pdf"
    )


# ---------- FILE UPLOAD ---------- #

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    path = f"data/{file.filename}"

    with open(path, "wb") as f:
        f.write(file.file.read())

    global rag
    rag = load_rag()

    return {"message": f"{file.filename} uploaded successfully"}


# ---------- CHAT ---------- #

@app.post("/chat")
def chat(query: Query):
    global rag

    if rag is None:
        rag = load_rag()

    try:
        answer = agent_respond(query.question, rag)
    except Exception as e:
        answer = f"Sorry, I encountered an error: {str(e)}"

    save_message(query.session_id, "user", query.question)
    save_message(query.session_id, "assistant", answer)

    return {"response": answer}