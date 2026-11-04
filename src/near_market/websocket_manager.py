from uuid import UUID
from fastapi import WebSocket

class ConnectionManager:
    
    def  __init__(self):
        self.active_connections: dict[UUID, list[WebSocket]] = {}
        
    async def connect( self, business_id: UUID,websocket: WebSocket ):
        await websocket.accept()
        
        if business_id not in self.active_connections:
            self.active_connections[business_id] = []
        self.active_connections[business_id].append(websocket)
            
    def disconnect(self, business_id: UUID, websocket: WebSocket):
        
        connections = self.active_connections.get(business_id, [])
        
        if websocket in connections:
            connections.remove(websocket)
            
        if not connections:
            self.active_connections.pop(business_id, None)
            
    async def send_to_business(self, business_id: UUID, message: dict):
        connections = self.active_connections.get(business_id, [])
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(business_id, websocket)
        
manager = ConnectionManager()