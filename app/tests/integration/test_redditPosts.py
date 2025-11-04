from datetime import date, datetime, timedelta
import json
import os
import pytest
from app.schemas.reddit_posts import RedditPost, RedditPostCreate
from app.services.redditPostsService import RedditPostsService
from app.settings.settings import get_settings

settings = get_settings()
        

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
            comments_per_post=settings.comments_per_post,
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

@pytest.mark.asyncio
async def test_005_get_reddit_posts_by_date_range_service(session):
    """
    Test to fetch Reddit posts within a specific date range.
    """
    reddit_posts_service = RedditPostsService(session)
    start_date = "2025-01-01"
    # end date is set to tomorrow to ensure we have posts
    end_date = (date.today() + timedelta(days=1)).isoformat()
    start_date_timestamp = int(datetime.fromisoformat(start_date).timestamp())
    end_date_timestamp = int(datetime.fromisoformat(end_date).timestamp())
    try:
        # load the posts from file
        posts_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_redditPosts",
            "test_005_posts_data.json"
        )
        with open(posts_file_path, 'r') as file:
            posts_data = json.load(file)
        # create posts in the database
        reddit_posts = [RedditPostCreate(**post) for post in posts_data]
        # create some posts in the database for the date range
        await reddit_posts_service.create_reddit_posts_service(reddit_posts)
        posts = await reddit_posts_service.get_reddit_posts_by_date_range_service(start_date_timestamp, end_date_timestamp)
        assert isinstance(posts, list), "Expected a list of posts."
        assert all(isinstance(post, RedditPost) for post in posts), "Expected all posts to be RedditPost objects."
        assert len(posts) > 0, "Expected at least one post within the date range."
    except Exception as e:
        pytest.fail(f"Failed to fetch Reddit posts by date range: {str(e)}")