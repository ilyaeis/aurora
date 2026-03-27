import asyncio
import time

from app.config import settings


class GameLoop:
    """Server-side game loop running at a fixed tick rate."""

    def __init__(self):
        self._running = False
        self._tick = 0
        self._task: asyncio.Task | None = None

    def start(self) -> asyncio.Task:
        self._running = True
        self._task = asyncio.create_task(self._run())
        return self._task

    def stop(self):
        self._running = False

    async def _run(self):
        tick_interval = 1.0 / settings.tick_rate

        while self._running:
            start = time.monotonic()
            self._tick += 1

            await self._update()

            elapsed = time.monotonic() - start
            sleep_time = max(0, tick_interval - elapsed)
            await asyncio.sleep(sleep_time)

    async def _update(self):
        """Called every tick. Process game state updates."""
        # Update connected player states
        from app.api.ws import connection_manager

        await connection_manager.broadcast_state()


game_loop = GameLoop()
