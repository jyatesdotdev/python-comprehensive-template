from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    PROJECT_NAME: str = "Python Template"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "A comprehensive Python project template."

    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    CORS_ORIGINS: list[str] = ["*"]

    SSE_MAX_EVENTS: int = 100

    API_KEY: str = "default-dev-key"
    API_KEY_NAME: str = "X-API-KEY"


settings = Settings()
