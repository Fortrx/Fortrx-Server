from fastapi import WebSocket
from app.services.pubsub import publish_message

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int,WebSocket] = {}
    async def connect(self,user_id:int,websocket:WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    def disconnect(self,user_id:int):
        self.active_connections.pop(user_id,None)
    async def send_to_user(self,user_id:int,data:dict):
        await publish_message(user_id,None) 
    def is_online(self,user_id:int):
        return user_id in self.active_connections

manager = ConnectionManager()