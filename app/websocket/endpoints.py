from fastapi import WebSocket, WebSocketDisconnect
from app.websocket.manager import manager

async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Просто поддерживаем соединение
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)