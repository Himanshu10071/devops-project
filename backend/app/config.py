from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IronPulse Gym API"
    app_version: str = "1.0.0"
    database_url: str = "postgresql+psycopg://ironpulse:ironpulse@localhost:5432/ironpulse"
    # Days before expiry at which a membership counts as "expiring soon".
    expiring_soon_days: int = 7
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
