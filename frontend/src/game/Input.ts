export type Direction = "up" | "down" | "left" | "right";

export class Input {
  private keys: Set<string> = new Set();

  constructor() {
    window.addEventListener("keydown", (e) => this.keys.add(e.key.toLowerCase()));
    window.addEventListener("keyup", (e) => this.keys.delete(e.key.toLowerCase()));
    window.addEventListener("blur", () => this.keys.clear());
  }

  isDown(key: string): boolean {
    return this.keys.has(key);
  }

  getMovement(): { dx: number; dy: number; facing: Direction | null } {
    let dx = 0;
    let dy = 0;
    let facing: Direction | null = null;

    if (this.isDown("w") || this.isDown("arrowup")) {
      dy = -1;
      facing = "up";
    }
    if (this.isDown("s") || this.isDown("arrowdown")) {
      dy = 1;
      facing = "down";
    }
    if (this.isDown("a") || this.isDown("arrowleft")) {
      dx = -1;
      facing = "left";
    }
    if (this.isDown("d") || this.isDown("arrowright")) {
      dx = 1;
      facing = "right";
    }

    // Normalize diagonal movement
    if (dx !== 0 && dy !== 0) {
      const len = Math.sqrt(dx * dx + dy * dy);
      dx /= len;
      dy /= len;
    }

    return { dx, dy, facing };
  }
}
