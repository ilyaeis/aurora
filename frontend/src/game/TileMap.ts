import { Container, Graphics } from "pixi.js";
import {
  TILE_SIZE,
  CHUNK_SIZE,
  CHUNK_PIXEL_SIZE,
  TILE_COLORS,
  BACKEND_URL,
} from "./constants";

interface ChunkData {
  x: number;
  y: number;
  biome: string;
  tiles: number[][];
  pois: Array<{ name: string; type: string; x: number; y: number }>;
  description: string | null;
}

export class TileMap {
  public container: Container;
  private loadedChunks: Map<string, Container> = new Map();
  private loadingChunks: Set<string> = new Set();

  constructor() {
    this.container = new Container();
  }

  private chunkKey(cx: number, cy: number): string {
    return `${cx},${cy}`;
  }

  /** Ensure chunks around player position are loaded */
  async ensureChunksAround(worldX: number, worldY: number) {
    const cx = Math.floor(worldX / CHUNK_PIXEL_SIZE);
    const cy = Math.floor(worldY / CHUNK_PIXEL_SIZE);

    // Load a 3x3 grid around the player's chunk
    for (let dx = -1; dx <= 1; dx++) {
      for (let dy = -1; dy <= 1; dy++) {
        const key = this.chunkKey(cx + dx, cy + dy);
        if (!this.loadedChunks.has(key) && !this.loadingChunks.has(key)) {
          this.loadChunk(cx + dx, cy + dy);
        }
      }
    }

    // Unload far chunks (keep 5x5 around player)
    for (const [key, chunkContainer] of this.loadedChunks) {
      const [kx, ky] = key.split(",").map(Number);
      if (Math.abs(kx - cx) > 2 || Math.abs(ky - cy) > 2) {
        this.container.removeChild(chunkContainer);
        chunkContainer.destroy();
        this.loadedChunks.delete(key);
      }
    }
  }

  private async loadChunk(cx: number, cy: number) {
    const key = this.chunkKey(cx, cy);
    this.loadingChunks.add(key);

    try {
      const resp = await fetch(`${BACKEND_URL}/api/world/chunk/${cx}/${cy}`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data: ChunkData = await resp.json();
      this.renderChunk(data);
    } catch (e) {
      console.error(`Failed to load chunk ${key}:`, e);
      // Render a fallback green chunk
      this.renderFallbackChunk(cx, cy);
    } finally {
      this.loadingChunks.delete(key);
    }
  }

  private renderChunk(data: ChunkData) {
    const key = this.chunkKey(data.x, data.y);

    // Don't re-render if already loaded
    if (this.loadedChunks.has(key)) return;

    const chunkContainer = new Container();
    chunkContainer.x = data.x * CHUNK_PIXEL_SIZE;
    chunkContainer.y = data.y * CHUNK_PIXEL_SIZE;

    // Render tiles as colored rectangles
    const gfx = new Graphics();
    for (let row = 0; row < CHUNK_SIZE; row++) {
      for (let col = 0; col < CHUNK_SIZE; col++) {
        const tileId = data.tiles[row]?.[col] ?? 0;
        const color = TILE_COLORS[tileId] ?? 0x4caf50;
        gfx.rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE);
        gfx.fill(color);
      }
    }

    // Draw tile grid lines
    gfx.setStrokeStyle({ width: 0.5, color: 0x000000, alpha: 0.08 });
    for (let i = 0; i <= CHUNK_SIZE; i++) {
      gfx.moveTo(i * TILE_SIZE, 0);
      gfx.lineTo(i * TILE_SIZE, CHUNK_PIXEL_SIZE);
      gfx.moveTo(0, i * TILE_SIZE);
      gfx.lineTo(CHUNK_PIXEL_SIZE, i * TILE_SIZE);
    }
    gfx.stroke();

    chunkContainer.addChild(gfx);

    // Render POIs as markers
    for (const poi of data.pois) {
      const marker = new Graphics();
      marker.circle(0, 0, 8);
      marker.fill(0xff9800);
      marker.setStrokeStyle({ width: 2, color: 0xffffff });
      marker.stroke();
      marker.x = poi.x * TILE_SIZE + TILE_SIZE / 2;
      marker.y = poi.y * TILE_SIZE + TILE_SIZE / 2;
      chunkContainer.addChild(marker);
    }

    this.container.addChild(chunkContainer);
    this.loadedChunks.set(key, chunkContainer);
  }

  private renderFallbackChunk(cx: number, cy: number) {
    const key = this.chunkKey(cx, cy);
    if (this.loadedChunks.has(key)) return;

    const chunkContainer = new Container();
    chunkContainer.x = cx * CHUNK_PIXEL_SIZE;
    chunkContainer.y = cy * CHUNK_PIXEL_SIZE;

    const gfx = new Graphics();
    gfx.rect(0, 0, CHUNK_PIXEL_SIZE, CHUNK_PIXEL_SIZE);
    gfx.fill(0x388e3c);
    chunkContainer.addChild(gfx);

    this.container.addChild(chunkContainer);
    this.loadedChunks.set(key, chunkContainer);
  }
}
