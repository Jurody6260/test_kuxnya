import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "KuxnyaCRM"
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/crm",
    )
    TEST_DATABASE_URL: str = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db",
    )
    JWT_SECRET: str = "DSBFBNFEHNRWGdgzash"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    API_V1_STR: str = "/api/v1"
    model_config = SettingsConfigDict(env_file=".env")

    class ConfigDict:
        env_file = ".env"


settings = Settings()
