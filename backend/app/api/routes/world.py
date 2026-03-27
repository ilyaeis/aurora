from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.game.world import WorldManager
from app.models.database import get_db
from app.models.world import WorldChunk

router = APIRouter()
world_manager = WorldManager()


class ChunkResponse(BaseModel):
    x: int
    y: int
    biome: str
    tiles: list
    pois: list
    description: str | None

    model_config = {"from_attributes": True}


@router.get("/chunk/{cx}/{cy}", response_model=ChunkResponse)
async def get_chunk(cx: int, cy: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WorldChunk).where(and_(WorldChunk.x == cx, WorldChunk.y == cy))
    )
    chunk = result.scalar_one_or_none()

    if not chunk:
        # Generate a new chunk (template fallback for now, AI later)
        chunk = await world_manager.generate_chunk(cx, cy, db)

    return chunk


@router.get("/chunks/around/{cx}/{cy}")
async def get_chunks_around(cx: int, cy: int, db: AsyncSession = Depends(get_db)):
    """Get a 3x3 grid of chunks centered on (cx, cy)."""
    chunks = []
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            nx, ny = cx + dx, cy + dy
            result = await db.execute(
                select(WorldChunk).where(and_(WorldChunk.x == nx, WorldChunk.y == ny))
            )
            chunk = result.scalar_one_or_none()
            if not chunk:
                chunk = await world_manager.generate_chunk(nx, ny, db)
            chunks.append(ChunkResponse.model_validate(chunk))
    return chunks
