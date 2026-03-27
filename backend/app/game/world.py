import random

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.world import WorldChunk

# Tile IDs for the template generator
TILE_GRASS = 0
TILE_WATER = 1
TILE_FOREST = 2
TILE_MOUNTAIN = 3
TILE_PATH = 4
TILE_SAND = 5

BIOMES = ["plains", "forest", "desert", "mountains", "swamp", "tundra"]

BIOME_TILE_WEIGHTS = {
    "plains": {TILE_GRASS: 0.7, TILE_PATH: 0.15, TILE_FOREST: 0.1, TILE_WATER: 0.05},
    "forest": {TILE_FOREST: 0.6, TILE_GRASS: 0.25, TILE_PATH: 0.1, TILE_WATER: 0.05},
    "desert": {TILE_SAND: 0.75, TILE_GRASS: 0.1, TILE_PATH: 0.1, TILE_MOUNTAIN: 0.05},
    "mountains": {TILE_MOUNTAIN: 0.5, TILE_GRASS: 0.2, TILE_FOREST: 0.15, TILE_PATH: 0.15},
    "swamp": {TILE_WATER: 0.4, TILE_GRASS: 0.35, TILE_FOREST: 0.2, TILE_PATH: 0.05},
    "tundra": {TILE_GRASS: 0.4, TILE_MOUNTAIN: 0.3, TILE_WATER: 0.2, TILE_PATH: 0.1},
}

POI_TYPES = ["village", "ruins", "camp", "shrine", "cave", "tower"]


class WorldManager:
    """Manages world state and chunk generation.

    Currently uses template-based generation.
    Will be replaced with AI generation in Phase 2.
    """

    async def generate_chunk(
        self, cx: int, cy: int, db: AsyncSession
    ) -> WorldChunk:
        """Generate a new chunk at coordinates (cx, cy) using templates."""
        # Spawn chunk (0,0) is always plains
        if cx == 0 and cy == 0:
            biome = "plains"
        else:
            biome = random.choice(BIOMES)

        tiles = self._generate_tiles(biome)
        pois = self._generate_pois(biome, cx, cy)
        description = f"A {biome} region at ({cx}, {cy})"

        chunk = WorldChunk(
            x=cx,
            y=cy,
            biome=biome,
            tiles=tiles,
            pois=pois,
            description=description,
            generated_by="template",
        )
        db.add(chunk)
        await db.commit()
        await db.refresh(chunk)
        return chunk

    def _generate_tiles(self, biome: str) -> list[list[int]]:
        """Generate a chunk_size x chunk_size grid of tile IDs."""
        size = settings.chunk_size
        weights = BIOME_TILE_WEIGHTS.get(biome, BIOME_TILE_WEIGHTS["plains"])
        tile_ids = list(weights.keys())
        tile_weights = list(weights.values())

        return [
            random.choices(tile_ids, weights=tile_weights, k=size)
            for _ in range(size)
        ]

    def _generate_pois(self, biome: str, cx: int, cy: int) -> list[dict]:
        """Maybe generate 0-2 points of interest in this chunk."""
        pois = []
        # 40% chance of at least one POI, spawn chunk always gets a village
        if cx == 0 and cy == 0:
            pois.append({
                "name": "Starting Village",
                "type": "village",
                "x": settings.chunk_size // 2,
                "y": settings.chunk_size // 2,
            })
        elif random.random() < 0.4:
            num_pois = random.randint(1, 2)
            for _ in range(num_pois):
                pois.append({
                    "name": f"{biome.title()} {random.choice(POI_TYPES).title()}",
                    "type": random.choice(POI_TYPES),
                    "x": random.randint(4, settings.chunk_size - 4),
                    "y": random.randint(4, settings.chunk_size - 4),
                })
        return pois
