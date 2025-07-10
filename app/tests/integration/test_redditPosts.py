from contextlib import asynccontextmanager
import pytest
from app.services.redditPostsService import RedditPostsService
from app.settings.settings import get_settings
from sqlalchemy import text

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
async def test_001_get_reddit_posts_user(session):
    try:
        """
        Test fetching posts from a specific Reddit user.
        """
        author = "spez"  # Example author, replace with a valid Reddit username
        reddit_service = RedditPostsService(session)
        posts = await reddit_service.get_reddit_posts_user_service(author)
        # should throw an exception if no posts are found
    except Exception as e:
        # make sure j6RHyQVBe2 is in the error message
        if "j6RHyQVBe2" in str(e):
            assert True, f"Successfully caught exception for user {author}: {str(e)}"
        else:
            assert False, f"Unexpected error for user {author}: {str(e)}"

@pytest.mark.asyncio
async def test_002_get_reddit_posts_from_subreddit(session):
    """
    Test fetching posts from a subreddit.
    """
    subreddit = settings.subreddits[0]
    posts_per_subreddit = settings.posts_per_subreddit
    subreddit_sort = settings.subreddit_sort
    
    reddit_service = RedditPostsService(session)
    posts = await reddit_service.get_reddit_posts_from_subreddit(subreddit, posts_per_subreddit, subreddit_sort)
    
    assert isinstance(posts, list), "Posts should be a list"
    assert len(posts) <= posts_per_subreddit, f"Expected at most {posts_per_subreddit} posts, got {len(posts)}"
    assert all("title" in post for post in posts), "Each post should have a title"

@pytest.mark.asyncio
async def test_003_get_posts_from_subreddits_service(session):
    """
    Test fetching posts from multiple subreddits.
    """
    try:
        reddit_service = RedditPostsService(session)
        result = await reddit_service.get_posts_from_subreddits_service(
            subreddits=settings.subreddits,
            posts_per_subreddit=settings.posts_per_subreddit,
            subreddit_sort=settings.subreddit_sort)
        assert isinstance(result, list), "Result should be a list of RedditPostCreate objects"
        assert len(result) > 0, "Expected to fetch posts from subreddits"
    except Exception as e:
        assert False, f"Failed to fetch posts from subreddits: {str(e)}"
    await shutdown_event()

@pytest.mark.asyncio
async def test_004_fetch_posts_and_comments_from_reddit_service(session):
    """
    Test fetching posts and comments from Reddit.
    """
    try:
        reddit_service = RedditPostsService(session)
        result = await reddit_service.fetch_posts_and_comments_from_reddit_service(
            subreddits=settings.subreddits,
            posts_per_subreddit=1,
            subreddit_sort=settings.subreddit_sort,
            comment_sort="top"
        )
        posts, comments = result.posts, result.comments
        assert isinstance(posts, list), "Posts should be a list of RedditPostCreate objects"
        assert isinstance(comments, list), "Comments should be a list of RedditCommentCreate objects"
        assert len(posts) > 0, "Expected to fetch posts from subreddits"
        assert len(comments) > 0, "Expected to fetch comments for the posts"
    except Exception as e:
        assert False, f"Failed to fetch posts and comments from Reddit: {str(e)}"
    await shutdown_event()