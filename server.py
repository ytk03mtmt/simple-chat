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
