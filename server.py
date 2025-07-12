from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from datetime import datetime

app = FastAPI()

# 静的ファイルを /static にマウント
app.mount("/static", StaticFiles(directory="static"), name="static")

# "/" にアクセスされたときは index.html を返すようにする
@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

clients: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("接続しました")
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            message = f"{now} {data}"
            print(f"送信: {message}")
            for client in clients:
                await client.send_text(message)
    except WebSocketDisconnect:
        print("切断されました")
        clients.remove(websocket)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from datetime import datetime
import os
import shutil

app = FastAPI()

# ファイル保存用ディレクトリ
UPLOAD_DIR = "uploaded"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 静的ファイルマウント
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

clients: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("接続しました")
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            message = f"{now} {data}"
            print(f"送信: {message}")
            for client in clients:
                await client.send_text(message)
    except WebSocketDisconnect:
        print("切断されました")
        clients.remove(websocket)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file.filename
