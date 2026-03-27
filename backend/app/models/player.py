from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.models.database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)

    # Position in world
    x = Column(Float, default=0.0)
    y = Column(Float, default=0.0)
    chunk_x = Column(Integer, default=0)
    chunk_y = Column(Integer, default=0)

    # Stats & progression
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    hp = Column(Integer, default=100)
    max_hp = Column(Integer, default=100)

    # AI-generated class (assigned after initial play period)
    class_data = Column(JSONB, nullable=True)  # {name, description, abilities, stats, visual_theme}

    # Inventory stored as JSON array
    inventory = Column(JSONB, default=list)

    # Equipment slots
    equipment = Column(JSONB, default=dict)  # {weapon, armor, accessory}

    # Stats: base + class bonuses
    stats = Column(JSONB, default=lambda: {"atk": 10, "def": 10, "spd": 10})

    # Behavior log for AI class assignment
    behavior_log = Column(JSONB, default=list)
