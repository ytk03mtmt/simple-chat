# server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from typing import List

app = FastAPI()
app.mount("/", StaticFiles(directory="static", html=True), name="static")

clients: List[WebSocket] = []

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

