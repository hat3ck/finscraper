import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from app.settings.settings import get_settings

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path, override=True)
print("Loaded environment variables from .env")
table_names = ["reddit_posts", "reddit_comments", "reddit_tokens",
               "currency_prices", "llm_providers", "reddit_sentiments",
               "ml_models", "orders", "wallets"]

settings = get_settings()

import pytest
from app.database import get_db_session, sessionmanager
@pytest.fixture(autouse=True)
async def reset_database_session_manager():
    # Ensure engine/sessionmaker are recreated for each test loop
    await sessionmanager.reset()
    yield
    await sessionmanager.reset()

@pytest.fixture
async def session():
    async for s in get_db_session():
        yield s
        

@pytest.fixture(scope="function", autouse=True)
async def clean_database():
    engine = create_async_engine(settings.database_url, future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        for table in table_names:
            await session.execute(text(f"DELETE FROM {table}"))
        await session.commit()

    yield

    async with async_session() as session:
        for table in table_names:
            await session.execute(text(f"DELETE FROM {table}"))
        await session.commit()

    await engine.dispose()