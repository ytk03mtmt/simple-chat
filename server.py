from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List

app = FastAPI()

# 静的ファイルは /static 以下に提供
app.mount("/static", StaticFiles(directory="static"), name="static")

clients: List[WebSocket] = []

@app.get("/")
async def get():
    return FileResponse("static/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("接続しました")
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"受信: {data}")
            for client in clients:
                if client != websocket:
                    await client.send_text(data)
    except WebSocketDisconnect:
        print("切断されました")
        clients.remove(websocket)
