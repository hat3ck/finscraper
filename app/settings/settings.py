from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os

class Settings(BaseSettings):
    env: str = os.getenv("ENV")
    app_port: int = int(os.getenv("APP_PORT", 8000))
    db_user: str = os.getenv("DB_USER")
    db_pass: str = os.getenv("DB_PASSWORD") # Must be provided in the environment
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", 5432))
    db_name: str = os.getenv("DB_NAME", "dev_db")
    echo_sql: bool = False
    project_name: str
    log_level: str = "DEBUG"
    debug_logs: bool = False
    subreddits: list[str] = ["CryptoCurrency", "Bitcoin", "CryptoMarkets", "BitcoinMarkets", "Altcoin", "CryptoTechnology", "CryptoCurrencyTrading", "CryptoNews"]
    posts_per_subreddit: int = 10
    subreddit_sort: str = "hot"
    comment_sort: str = "top"
    comments_per_post: int = 20
    comment_depth: int = 3
    reddit_client_id: str = os.getenv("REDDIT_CLIENT_ID")
    reddit_client_secret: str = os.getenv("REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = os.getenv("REDDIT_USER_AGENT", "testscript:v1.0.1 (by /u/hat3ck)")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), f".env.{env}"),
        env_file_encoding="utf-8"
    )

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("postgresql+asyncpg", "postgresql")

@lru_cache
def get_settings():
    return Settings()