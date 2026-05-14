from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    EVENTFINDA_USERNAME: str
    EVENTFINDA_PASSWORD: str
    TICKETMASTER_API_KEY: str
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL_SYNC: str = ""
    DATABASE_URL: str = ""
    GOOGLE_MAPS_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

    def get_allowed_origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()