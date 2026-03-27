from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Aurora"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://aurora:aurora@localhost:5432/aurora"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # AI / Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    ollama_fast_model: str = "gemma2:2b"

    # Game
    tick_rate: int = 20  # server ticks per second
    chunk_size: int = 32  # tiles per chunk side
    tile_size: int = 32  # pixels per tile

    # Auth
    secret_key: str = "dev-secret-change-in-production"
    access_token_expire_minutes: int = 1440  # 24 hours

    model_config = {"env_prefix": "AURORA_"}


settings = Settings()
