from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.models.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    item_type = Column(String(50), nullable=False)  # weapon, armor, accessory, consumable
    rarity = Column(String(20), default="common")  # common, uncommon, rare, epic, legendary
    stats = Column(JSONB, default=dict)  # {atk: 5, def: 0, ...}
    description = Column(Text, nullable=True)
    lore = Column(Text, nullable=True)
    generated_by = Column(String(100), default="template")


class Enemy(Base):
    __tablename__ = "enemies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_x = Column(Integer, nullable=False)
    chunk_y = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    level = Column(Integer, default=1)
    stats = Column(JSONB, default=dict)  # {hp, atk, def, spd}
    abilities = Column(JSONB, default=list)  # [{name, type, damage, description}]
    loot_table = Column(JSONB, default=list)  # [{item_id, drop_chance}]
    sprite_desc = Column(Text, nullable=True)  # AI description for future sprite gen
    generated_by = Column(String(100), default="template")
