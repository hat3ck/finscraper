from contextlib import asynccontextmanager
import pytest
from app.schemas.reddit_tokens import RedditTokenCreate, RedditToken
from app.services.redditTokenService import RedditTokenService
from app.settings.settings import get_settings
from sqlalchemy import text
from .conftest import table_names
import os
import json

from app.database import get_db_session

settings = get_settings()

# Initialize a session for testing
@asynccontextmanager
async def test_session():
    async for session in get_db_session():
        yield session

@pytest.fixture
async def session():
    async with test_session() as db_session:
        yield db_session

async def shutdown_event():
    # remove data from the database after tests
    gen = get_db_session()
    try:
        session = await anext(gen)
        for table in table_names:
            await session.execute(text(f"DELETE FROM {table}"))
        await session.commit()
    finally:
        await gen.aclose()
        

@pytest.mark.asyncio
async def test_000():
    """
    Test to ensure the test suite is running.
    """
    assert True, "Test suite is running correctly."

@pytest.mark.asyncio
async def test_001_get_reddit_token(session):
    try:
        reddit_token_service = RedditTokenService(session)
        token = await reddit_token_service.get_reddit_token()
        assert isinstance(token, str), "Expected a string token."
    except Exception as e:
        pytest.fail(f"Failed to get Reddit token: {str(e)}")