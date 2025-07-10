from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from typing import List
from datetime import datetime  # ←追加

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
            now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")  # ←時刻追加
            message = f"{now} {data}"  # ←元のメッセージに時刻を付ける
            print(f"送信: {message}")
            for client in clients:
                await client.send_text(message)
    except WebSocketDisconnect:
        print("切断されました")
        clients.remove(websocket)
