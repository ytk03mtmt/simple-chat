from fastapi import FastAPI, Depends, Request, WebSocket, WebSocketDisconnect, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Dict
import uuid

from models import User
from database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# セッション管理（メモリ上）
session_tokens: Dict[str, str] = {}
active_users: Dict[str, WebSocket] = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, session_token: str = Cookie(default=None)):
    username = session_tokens.get(session_token)
    if not username:
        return RedirectResponse("/login")
    return templates.TemplateResponse("index.html", {"request": request, "username": username})

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=username, password=password).first()
    if user:
        session_token = str(uuid.uuid4())
        session_tokens[session_token] = username
        response = RedirectResponse("/", status_code=302)
        response.set_cookie(key="session_token", value=session_token)
        return response
    return HTMLResponse("Invalid credentials", status_code=401)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_token: str = Cookie(default=None)):
    username = session_tokens.get(session_token)
    if not username:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    active_users[username] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            for user, ws in active_users.items():
                if user != username:
                    await ws.send_text(f"{username}: {data}")
    except WebSocketDisconnect:
        del active_users[username]
