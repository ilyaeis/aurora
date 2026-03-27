import { Container, Graphics, Text } from "pixi.js";
import { TILE_SIZE, MOVE_SPEED } from "./constants";
import type { Direction } from "./Input";

export class Player {
  public x: number;
  public y: number;
  public facing: Direction = "down";
  public container: Container;
  public id: number;
  public name: string;
  public isLocal: boolean;

  private body: Graphics;
  private nameTag: Text;

  constructor(id: number, name: string, x: number, y: number, isLocal: boolean) {
    this.id = id;
    this.name = name;
    this.x = x;
    this.y = y;
    this.isLocal = isLocal;

    this.container = new Container();

    // Player body (colored rectangle placeholder)
    this.body = new Graphics();
    this.drawBody(isLocal ? 0x42a5f5 : 0xef5350);
    this.container.addChild(this.body);

    // Name tag above player
    this.nameTag = new Text({
      text: name,
      style: {
        fontSize: 11,
        fill: 0xffffff,
        fontFamily: "monospace",
        align: "center",
      },
    });
    this.nameTag.anchor.set(0.5, 1);
    this.nameTag.y = -2;
    this.container.addChild(this.nameTag);

    this.updatePosition();
  }

  private drawBody(color: number) {
    this.body.rect(-TILE_SIZE / 2 + 4, 0, TILE_SIZE - 8, TILE_SIZE - 4);
    this.body.fill(color);
    // Direction indicator (small triangle)
    this.body.rect(-2, TILE_SIZE - 6, 4, 4);
    this.body.fill(0xffffff);
  }

  move(dx: number, dy: number, facing: Direction | null) {
    this.x += dx * MOVE_SPEED;
    this.y += dy * MOVE_SPEED;
    if (facing) this.facing = facing;
    this.updatePosition();
  }

  setPosition(x: number, y: number, facing?: Direction) {
    this.x = x;
    this.y = y;
    if (facing) this.facing = facing;
    this.updatePosition();
  }

  /** Smoothly interpolate towards target position (for remote players) */
  lerpTo(targetX: number, targetY: number, factor: number = 0.2) {
    this.x += (targetX - this.x) * factor;
    this.y += (targetY - this.y) * factor;
    this.updatePosition();
  }

  private updatePosition() {
    this.container.x = this.x;
    this.container.y = this.y;
  }
}
