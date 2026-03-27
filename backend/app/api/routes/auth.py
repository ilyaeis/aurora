from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.database import get_db
from app.models.player import Player

router = APIRouter()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


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
    is_admin: bool = False


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
        password_hash=hash_password(req.password),
        name=req.name,
    )
    db.add(player)
    await db.commit()
    await db.refresh(player)

    return TokenResponse(
        access_token=create_token(player.id),
        player_id=player.id,
        name=player.name,
        is_admin=player.is_admin,
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Player).where(Player.username == req.username))
    player = result.scalar_one_or_none()

    if not player or not verify_password(req.password, player.password_hash):
        raise HTTPException(401, "Invalid credentials")

    return TokenResponse(
        access_token=create_token(player.id),
        player_id=player.id,
        name=player.name,
        is_admin=player.is_admin,
    )
