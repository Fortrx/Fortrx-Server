from fastapi import APIRouter,WebSocket,WebSocketDisconnect,Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crypto import decode_access_token
from app.services import manager,subscribe_to_user,unsubscribe_from_user
import asyncio,websockets,json

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    user_id:int,
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=1008)
        return
    token_user_id = int(payload.get("sub"))
    if token_user_id!=user_id:
        await websocket.close(code=1008)
        return
    await manager.connect(user_id,websocket)
    pubsub,r = await subscribe_to_user(user_id)
    async def redis_listner():
        try:
            while True:
                text = await websocket.receive_text()
                if text == "ping":
                    await websocket.send_text("pong")
        except WebSocketDisconnect:
            pass
    
    redis_task = asyncio.create_task(redis_listner())
    ws_task = asyncio.create_task(ws_listner())
    
    done,pending = await asyncio.wait(
        [redis_task,ws_task],
        return_when=asyncio.FIRST_COMPLETED
    )
    for task in pending:
        task.cancel()
    manager.disconnect(user_id)
    await unsubscribe_from_user(pubsub,r)