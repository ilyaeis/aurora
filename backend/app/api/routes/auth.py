from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.database import get_db
from app.models.player import Player

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    player_id: int
    name: str


def create_token(player_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(player_id), "exp": expire},
        settings.secret_key,
        algorithm="HS256",
    )


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Player).where(Player.username == req.username))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Username already taken")

    player = Player(
        username=req.username,
        password_hash=pwd_context.hash(req.password),
        name=req.name,
    )
    db.add(player)
    await db.commit()
    await db.refresh(player)

    return TokenResponse(
        access_token=create_token(player.id),
        player_id=player.id,
        name=player.name,
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Player).where(Player.username == req.username))
    player = result.scalar_one_or_none()

    if not player or not pwd_context.verify(req.password, player.password_hash):
        raise HTTPException(401, "Invalid credentials")

    return TokenResponse(
        access_token=create_token(player.id),
        player_id=player.id,
        name=player.name,
    )
