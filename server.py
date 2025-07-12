# server.py
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from datetime import datetime
import shutil

app = FastAPI()
app.mount("/", StaticFiles(directory="static", html=True), name="static")

clients: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            username = data.get("username")
            message = data.get("message")
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            if message:
                msg = f'{timestamp} {username}: {message}'
                for client in clients:
                    await client.send_text(msg)
    except WebSocketDisconnect:
        clients.remove(websocket)

@app.post("/upload")
async def upload_file(file: UploadFile, username: str = Form(...)):
    filename = file.filename
    save_path = f"static/uploads/{filename}"
    os.makedirs("static/uploads", exist_ok=True)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    message = f'{timestamp} {username}: FILE: <a href="/uploads/{filename}" download>{filename}</a>'
    for client in clients:
        await client.send_text(message)
    return {"result": "ok"}
