export const TILE_SIZE = 32;
export const CHUNK_SIZE = 32; // tiles per chunk side
export const CHUNK_PIXEL_SIZE = TILE_SIZE * CHUNK_SIZE; // 1024px

export const MOVE_SPEED = 3; // pixels per frame

// Tile types matching backend
export const TILE_GRASS = 0;
export const TILE_WATER = 1;
export const TILE_FOREST = 2;
export const TILE_MOUNTAIN = 3;
export const TILE_PATH = 4;
export const TILE_SAND = 5;

// Tile colors (placeholder until sprites)
export const TILE_COLORS: Record<number, number> = {
  [TILE_GRASS]: 0x4caf50,
  [TILE_WATER]: 0x2196f3,
  [TILE_FOREST]: 0x2e7d32,
  [TILE_MOUNTAIN]: 0x795548,
  [TILE_PATH]: 0xd2b48c,
  [TILE_SAND]: 0xfdd835,
};

export const BACKEND_URL = "http://localhost:8000";
export const WS_URL = "ws://localhost:8000";
