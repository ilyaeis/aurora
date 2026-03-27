from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from app.models.database import Base


class WorldChunk(Base):
    __tablename__ = "world_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    biome = Column(String(50), nullable=False)
    tiles = Column(JSONB, nullable=False)  # 32x32 array of tile IDs
    pois = Column(JSONB, default=list)  # [{name, type, x, y}]
    description = Column(Text, nullable=True)
    generated_by = Column(String(100), default="template")  # model name or "template"
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        # Unique constraint on chunk coordinates
        {"sqlite_autoincrement": True},
    )


class NPC(Base):
    __tablename__ = "npcs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_x = Column(Integer, nullable=False)
    chunk_y = Column(Integer, nullable=False)
    x = Column(Float, nullable=False)  # position within chunk
    y = Column(Float, nullable=False)
    name = Column(String(100), nullable=False)
    race = Column(String(50), default="human")
    role = Column(String(50), default="villager")  # merchant, guard, quest_giver, etc.
    personality = Column(JSONB, default=dict)  # {traits: [], mood, goals}
    dialogue = Column(JSONB, default=list)  # [{text, responses: [{text, next}]}]
    generated_by = Column(String(100), default="template")


class WorldEvent(Base):
    __tablename__ = "world_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(50), nullable=False)  # dragon_sighting, plague, festival, etc.
    effects = Column(JSONB, default=dict)
    start_time = Column(DateTime, server_default=func.now())
    end_time = Column(DateTime, nullable=True)
    active = Column(Integer, default=1)
