import { Container } from "pixi.js";

export class Camera {
  private target: { x: number; y: number } | null = null;
  private screenWidth: number;
  private screenHeight: number;

  constructor(
    private container: Container,
    screenWidth: number,
    screenHeight: number
  ) {
    this.screenWidth = screenWidth;
    this.screenHeight = screenHeight;
  }

  setTarget(target: { x: number; y: number }) {
    this.target = target;
  }

  resize(width: number, height: number) {
    this.screenWidth = width;
    this.screenHeight = height;
  }

  update() {
    if (!this.target) return;

    // Center the camera on the target
    this.container.x = -this.target.x + this.screenWidth / 2;
    this.container.y = -this.target.y + this.screenHeight / 2;
  }

  /** Convert screen coordinates to world coordinates */
  screenToWorld(screenX: number, screenY: number): { x: number; y: number } {
    return {
      x: screenX - this.container.x,
      y: screenY - this.container.y,
    };
  }
}
