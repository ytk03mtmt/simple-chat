import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import shutil

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

connections = set()

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            message = f"{now} {data}"
            for conn in connections:
                await conn.send_text(message)
    except WebSocketDisconnect:
        connections.remove(websocket)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    message = f'{now} FILE:<a href="/static/uploads/{file.filename}" target="_blank">{file.filename}</a>'

    for conn in connections:
        await conn.send_text(message)
    return {"filename": file.filename}
