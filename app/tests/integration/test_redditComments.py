from contextlib import asynccontextmanager
import pytest
from app.schemas.reddit_comments import RedditCommentCreate
from app.services.redditCommentsService import RedditCommentsService
from app.settings.settings import get_settings
from sqlalchemy import text
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
        table_names = ["reddit_posts", "reddit_comments"]
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
async def test_001_get_reddit_comments_post_service(session):
    """
    Test to fetch Reddit comments for a specific post.
    """
    reddit_comments_service = RedditCommentsService(session)
    try:
        # load the comments from file under tests/integration/data/test_redditComments/test_001_comments_data.json
        comments_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_redditComments",
            "test_001_comments_data.json"
        )
        with open(comments_file_path, 'r') as file:
            comments_data = json.load(file)
        # create comments in the database
        reddit_comments = [RedditCommentCreate(**comment) for comment in comments_data]
        await reddit_comments_service.create_reddit_comments_service(reddit_comments)
        comments = await reddit_comments_service.get_reddit_comments_post_service(reddit_comments[0].post_id)
        assert isinstance(comments, list), "Expected a list of comments."
        assert len(comments) > 0, "Expected at least one comment."
    except Exception as e:
        pytest.fail(f"Failed to fetch Reddit comments: {str(e)}")
        
    await shutdown_event()