import { Application, Container } from "pixi.js";
import { Camera } from "./Camera";
import { Input } from "./Input";
import { Player } from "./Player";
import { TileMap } from "./TileMap";
import { CHUNK_PIXEL_SIZE, CHUNK_SIZE, TILE_SIZE } from "./constants";
import { NetworkClient } from "../network/Socket";

export class Engine {
  private app: Application;
  private worldContainer: Container;
  private camera: Camera;
  private input: Input;
  private tileMap: TileMap;
  private localPlayer: Player | null = null;
  private remotePlayers: Map<number, Player> = new Map();
  private network: NetworkClient;
  private playerId: number;
  private playerName: string;
  private lastChunkLoadX: number = -999;
  private lastChunkLoadY: number = -999;
  private moveThrottle: number = 0;

  constructor(playerId: number, playerName: string, token: string) {
    this.app = new Application();
    this.playerId = playerId;
    this.playerName = playerName;

    this.worldContainer = new Container();
    this.input = new Input();
    this.tileMap = new TileMap();
    this.camera = new Camera(this.worldContainer, 0, 0);

    this.network = new NetworkClient(playerId, playerName, token);
    this.network.onMessage = this.handleNetworkMessage.bind(this);
  }

  async init(canvas: HTMLCanvasElement) {
    await this.app.init({
      canvas,
      resizeTo: window,
      backgroundColor: 0x1a1a2e,
      antialias: false,
    });

    // World container holds tilemap + players
    this.worldContainer.addChild(this.tileMap.container);
    this.app.stage.addChild(this.worldContainer);

    this.camera.resize(this.app.screen.width, this.app.screen.height);

    // Spawn local player at center of spawn chunk
    const spawnX = CHUNK_SIZE * TILE_SIZE / 2;
    const spawnY = CHUNK_SIZE * TILE_SIZE / 2;
    this.localPlayer = new Player(this.playerId, this.playerName, spawnX, spawnY, true);
    this.worldContainer.addChild(this.localPlayer.container);
    this.camera.setTarget(this.localPlayer);

    // Load initial chunks
    await this.tileMap.ensureChunksAround(spawnX, spawnY);

    // Connect to server
    this.network.connect();

    // Game loop
    this.app.ticker.add(this.update.bind(this));

    // Handle resize
    window.addEventListener("resize", () => {
      this.camera.resize(this.app.screen.width, this.app.screen.height);
    });
  }

  private update() {
    if (!this.localPlayer) return;

    // Handle input
    const { dx, dy, facing } = this.input.getMovement();
    if (dx !== 0 || dy !== 0) {
      this.localPlayer.move(dx, dy, facing);

      // Throttle network updates (every 3 frames)
      this.moveThrottle++;
      if (this.moveThrottle >= 3) {
        this.moveThrottle = 0;
        this.network.sendMove(
          this.localPlayer.x,
          this.localPlayer.y,
          this.localPlayer.facing
        );
      }
    }

    // Check if we need to load new chunks
    const playerChunkX = Math.floor(this.localPlayer.x / CHUNK_PIXEL_SIZE);
    const playerChunkY = Math.floor(this.localPlayer.y / CHUNK_PIXEL_SIZE);
    if (playerChunkX !== this.lastChunkLoadX || playerChunkY !== this.lastChunkLoadY) {
      this.lastChunkLoadX = playerChunkX;
      this.lastChunkLoadY = playerChunkY;
      this.tileMap.ensureChunksAround(this.localPlayer.x, this.localPlayer.y);
    }

    // Interpolate remote players
    for (const remote of this.remotePlayers.values()) {
      // Interpolation happens via lerpTo called in handleNetworkMessage
    }

    // Update camera
    this.camera.update();
  }

  private handleNetworkMessage(msg: any) {
    switch (msg.type) {
      case "init":
        // Set up existing players
        for (const p of msg.players) {
          if (p.id !== this.playerId) {
            this.addRemotePlayer(p);
          }
        }
        break;

      case "state":
        // Update all player positions
        for (const p of msg.players) {
          if (p.id === this.playerId) continue;
          const remote = this.remotePlayers.get(p.id);
          if (remote) {
            remote.lerpTo(p.x, p.y);
            if (p.facing) remote.facing = p.facing;
          } else {
            this.addRemotePlayer(p);
          }
        }
        break;

      case "player_joined":
        if (msg.player.id !== this.playerId) {
          this.addRemotePlayer(msg.player);
        }
        break;

      case "player_left":
        this.removeRemotePlayer(msg.player_id);
        break;

      case "chat":
        // Dispatch chat event for UI to handle
        window.dispatchEvent(
          new CustomEvent("game:chat", {
            detail: { name: msg.name, text: msg.text },
          })
        );
        break;
    }
  }

  private addRemotePlayer(data: any) {
    if (this.remotePlayers.has(data.id)) return;
    const remote = new Player(data.id, data.name, data.x, data.y, false);
    this.remotePlayers.set(data.id, remote);
    this.worldContainer.addChild(remote.container);
  }

  private removeRemotePlayer(id: number) {
    const remote = this.remotePlayers.get(id);
    if (remote) {
      this.worldContainer.removeChild(remote.container);
      remote.container.destroy();
      this.remotePlayers.delete(id);
    }
  }

  sendChat(text: string) {
    this.network.sendChat(text);
  }

  destroy() {
    this.network.disconnect();
    this.app.destroy(true);
  }
}
