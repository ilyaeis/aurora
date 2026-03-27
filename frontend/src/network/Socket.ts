import { WS_URL } from "../game/constants";

export class NetworkClient {
  private ws: WebSocket | null = null;
  private playerId: number;
  private playerName: string;
  private token: string;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  public onMessage: ((msg: any) => void) | null = null;

  constructor(playerId: number, playerName: string, token: string) {
    this.playerId = playerId;
    this.playerName = playerName;
    this.token = token;
  }

  connect() {
    const url = `${WS_URL}/ws/${this.playerId}?name=${encodeURIComponent(this.playerName)}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log("[Aurora] Connected to server");
    };

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        this.onMessage?.(msg);
      } catch (e) {
        console.error("[Aurora] Failed to parse message:", e);
      }
    };

    this.ws.onclose = () => {
      console.log("[Aurora] Disconnected, reconnecting in 3s...");
      this.reconnectTimer = setTimeout(() => this.connect(), 3000);
    };

    this.ws.onerror = (err) => {
      console.error("[Aurora] WebSocket error:", err);
    };
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.ws = null;
  }

  private send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  sendMove(x: number, y: number, facing: string) {
    this.send({ type: "move", x, y, facing });
  }

  sendChat(text: string) {
    this.send({ type: "chat", text });
  }
}
