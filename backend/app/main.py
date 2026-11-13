from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.middleware import RateLimitMiddleware
from app.routers import auth, leads, deals, conversations, tasks, workflows, analytics, integrations, organizations
import app.models  # ensure all models are registered

app = FastAPI(title="Customer Support CRM API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, calls=200, period=60)

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(deals.router)
app.include_router(conversations.router)
app.include_router(tasks.router)
app.include_router(workflows.router)
app.include_router(analytics.router)
app.include_router(integrations.router)
app.include_router(organizations.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Customer Support CRM"}


# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, org_id: str):
        await websocket.accept()
        if org_id not in self.active_connections:
            self.active_connections[org_id] = []
        self.active_connections[org_id].append(websocket)

    def disconnect(self, websocket: WebSocket, org_id: str):
        if org_id in self.active_connections:
            self.active_connections[org_id].remove(websocket)

    async def broadcast(self, org_id: str, message: dict):
        if org_id in self.active_connections:
            for ws in self.active_connections[org_id]:
                await ws.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws/{org_id}")
async def websocket_endpoint(websocket: WebSocket, org_id: str):
    await manager.connect(websocket, org_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(org_id, {"type": "notification", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket, org_id)
