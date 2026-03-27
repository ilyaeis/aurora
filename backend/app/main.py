from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, players, world
from app.api.ws import router as ws_router
from app.config import settings
from app.game.loop import game_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    loop_task = game_loop.start()
    yield
    # Shutdown
    game_loop.stop()
    if loop_task:
        loop_task.cancel()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_router)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(players.router, prefix="/api/players", tags=["players"])
app.include_router(world.router, prefix="/api/world", tags=["world"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "game": settings.app_name}
