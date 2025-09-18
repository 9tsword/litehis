from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = Field(default="LiteHIS")
    database_url: str = Field(default="sqlite:///./litehis.db")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
