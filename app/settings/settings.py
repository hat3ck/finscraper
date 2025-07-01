from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    env: str = os.getenv("ENV", "dev")
    app_port: int = int(os.getenv("APP_PORT", 8000))
    db_user: str = os.getenv("DB_USER", "dev-user")
    db_pass: str = os.getenv("DB_PASSWORD") # Must be provided in the environment
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", 5432))
    db_name: str = os.getenv("DB_NAME", "dev_db")
    echo_sql: bool = True
    project_name: str
    log_level: str = "DEBUG"
    debug_logs: bool = True

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), f".env.{env}"),
        env_file_encoding="utf-8"
    )

settings = Settings()