
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# settings.py está dentro de src/near_market/
# Subimos tres niveles para llegar a la raíz de Buskalo.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str
    test_database_url: str | None = None

    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, gt=0)

    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173"
    )

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()