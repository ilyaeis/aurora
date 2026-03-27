from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.database import get_db
from app.models.player import Player

router = APIRouter()


class PlayerResponse(BaseModel):
    id: int
    name: str
    x: float
    y: float
    chunk_x: int
    chunk_y: int
    level: int
    xp: int
    hp: int
    max_hp: int
    class_data: dict | None
    stats: dict

    model_config = {"from_attributes": True}


async def get_current_player(token: str, db: AsyncSession) -> Player:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        player_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(401, "Invalid token")

    result = await db.execute(select(Player).where(Player.id == player_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(404, "Player not found")
    return player


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Player).where(Player.id == player_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(404, "Player not found")
    return player
