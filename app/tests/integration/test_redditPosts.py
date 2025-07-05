import pytest
from app.services.redditPostsService import get_reddit_posts_user_service, get_reddit_posts_from_subreddit, get_posts_from_subreddits_service
from app.settings.settings import get_settings
from sqlalchemy import text

from app.database import get_db_session

settings = get_settings()

# Initialize a session for testing
@pytest.fixture(scope="module")
async def session():
    async with get_db_session() as db_session:
        yield db_session

async def shutdown_event():
    # remove data from the database after tests
    async with get_db_session() as db_session:
        table_names = ["reddit_posts", "reddit_comments"]
        for table in table_names:
            await db_session.execute(text(f"DELETE FROM {table}"))
        await db_session.commit()
        

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
        posts = await get_reddit_posts_user_service(session, author)
        # should throw an exception if no posts are found
    except Exception as e:
        # make sure j6RHyQVBe2 is in the error message
        if "j6RHyQVBe2" in str(e):
            assert True, f"Successfully caught exception for user {author}: {str(e)}"
        else:
            assert False, f"Unexpected error for user {author}: {str(e)}"

@pytest.mark.asyncio
async def test_002_get_reddit_posts_from_subreddit():
    """
    Test fetching posts from a subreddit.
    """
    subreddit = settings.subreddits[0]
    posts_per_subreddit = settings.posts_per_subreddit
    subreddit_sort = settings.subreddit_sort
    
    posts = await get_reddit_posts_from_subreddit(subreddit, posts_per_subreddit, subreddit_sort)
    
    assert isinstance(posts, list), "Posts should be a list"
    assert len(posts) <= posts_per_subreddit, f"Expected at most {posts_per_subreddit} posts, got {len(posts)}"
    assert all("title" in post for post in posts), "Each post should have a title"

@pytest.mark.asyncio
async def test_003_get_posts_from_subreddits_service(session):
    """
    Test fetching posts from multiple subreddits.
    """
    try:
        result = await get_posts_from_subreddits_service(
            session,
            subreddits=settings.subreddits,
            posts_per_subreddit=settings.posts_per_subreddit,
            subreddit_sort=settings.subreddit_sort)
        await shutdown_event()
        assert isinstance(result, str), "Result should be a string message"
        assert "Successfully fetched and saved posts" in result, "Expected success message in result"
    except Exception as e:
        assert False, f"Failed to fetch posts from subreddits: {str(e)}"