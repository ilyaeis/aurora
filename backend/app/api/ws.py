import json
from dataclasses import dataclass, field

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@dataclass
class PlayerState:
    player_id: int
    name: str
    x: float = 0.0
    y: float = 0.0
    chunk_x: int = 0
    chunk_y: int = 0
    facing: str = "down"

    def to_dict(self) -> dict:
        return {
            "id": self.player_id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "chunk_x": self.chunk_x,
            "chunk_y": self.chunk_y,
            "facing": self.facing,
        }


class ConnectionManager:
    def __init__(self):
        self.connections: dict[int, WebSocket] = {}  # player_id -> websocket
        self.player_states: dict[int, PlayerState] = {}  # player_id -> state

    async def connect(self, websocket: WebSocket, player_id: int, name: str):
        await websocket.accept()
        self.connections[player_id] = websocket
        self.player_states[player_id] = PlayerState(player_id=player_id, name=name)

        # Notify all players about the new connection
        await self.broadcast(
            {"type": "player_joined", "player": self.player_states[player_id].to_dict()}
        )

    def disconnect(self, player_id: int):
        self.connections.pop(player_id, None)
        self.player_states.pop(player_id, None)

    async def broadcast(self, message: dict, exclude: int | None = None):
        data = json.dumps(message)
        disconnected = []
        for pid, ws in self.connections.items():
            if pid == exclude:
                continue
            try:
                await ws.send_text(data)
            except Exception:
                disconnected.append(pid)
        for pid in disconnected:
            self.disconnect(pid)

    async def send_to(self, player_id: int, message: dict):
        ws = self.connections.get(player_id)
        if ws:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                self.disconnect(player_id)

    async def broadcast_state(self):
        """Send all player positions to all connected clients."""
        if not self.connections:
            return

        players = [state.to_dict() for state in self.player_states.values()]
        await self.broadcast({"type": "state", "players": players})

    def get_players_in_chunk(self, chunk_x: int, chunk_y: int) -> list[PlayerState]:
        return [
            s
            for s in self.player_states.values()
            if s.chunk_x == chunk_x and s.chunk_y == chunk_y
        ]


connection_manager = ConnectionManager()


@router.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: int):
    # In production, validate token here
    name = websocket.query_params.get("name", f"Player_{player_id}")
    await connection_manager.connect(websocket, player_id, name)

    try:
        # Send initial state to the connecting player
        await connection_manager.send_to(
            player_id,
            {
                "type": "init",
                "your_id": player_id,
                "players": [s.to_dict() for s in connection_manager.player_states.values()],
            },
        )

        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg["type"] == "move":
                state = connection_manager.player_states.get(player_id)
                if state:
                    state.x = msg["x"]
                    state.y = msg["y"]
                    state.facing = msg.get("facing", state.facing)

                    # Update chunk if player crossed boundary
                    from app.config import settings

                    new_cx = int(state.x // settings.chunk_size)
                    new_cy = int(state.y // settings.chunk_size)
                    if new_cx != state.chunk_x or new_cy != state.chunk_y:
                        state.chunk_x = new_cx
                        state.chunk_y = new_cy
                        await connection_manager.send_to(
                            player_id,
                            {"type": "chunk_changed", "chunk_x": new_cx, "chunk_y": new_cy},
                        )

            elif msg["type"] == "chat":
                await connection_manager.broadcast(
                    {
                        "type": "chat",
                        "player_id": player_id,
                        "name": name,
                        "text": msg.get("text", ""),
                    }
                )

    except WebSocketDisconnect:
        connection_manager.disconnect(player_id)
        await connection_manager.broadcast(
            {"type": "player_left", "player_id": player_id}
        )
