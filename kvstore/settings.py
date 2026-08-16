from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KVSTORE_", env_file=".env")

    HOST: str = "[::]"
    PORT: int = 8000

    LRU_CAPACITY: int = 10

    SHUTDOWN_GRACE_SECONDS: float = 5.0


settings = Settings()
