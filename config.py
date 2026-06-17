from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    AIT_BASE_URL: str

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()