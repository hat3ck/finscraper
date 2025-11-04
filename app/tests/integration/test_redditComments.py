import pytest
from datetime import date, timedelta, datetime
from app.schemas.reddit_comments import RedditCommentCreate, RedditComment
from app.services.redditCommentsService import RedditCommentsService
from app.settings.settings import get_settings
import os
import json

settings = get_settings()
        

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
        

@pytest.mark.asyncio
async def test_002_get_reddit_comments_from_reddit(session):
    """
    Test to fetch Reddit comments directly from Reddit API.
    """
    reddit_comments_service = RedditCommentsService(session)
    # Confirmed post_id is valid
    post_id = "1ltnw74"
    try:
        comments = await reddit_comments_service.fetch_comments_from_reddit(post_id)
        assert isinstance(comments, list), "Expected a list of comments."
        assert len(comments) > 0, "Expected at least one comment."
        # make sure comments can be converted to RedditCommentCreate schema
        converted_comments = reddit_comments_service.convert_comments_to_schema(post_id, comments)
        assert isinstance(converted_comments, list), "Expected a list of converted comments."
        assert len(converted_comments) > 0, "Expected at least one valid comment."
    except Exception as e:
        pytest.fail(f"Failed to fetch Reddit comments from Reddit API: {str(e)}")

@pytest.mark.asyncio
async def test_003_fetch_comments_from_reddit_service(session):
    """
    Test to fetch comments for a post from reddit using the service.
    """
    reddit_comments_service = RedditCommentsService(session)
    post_id = "1ltnw74"
    try:
        result = await reddit_comments_service.fetch_comments_from_reddit_service(post_id)
        assert isinstance(result, list), "Expected a list of RedditCommentCreate objects."
        assert len(result) > 0, "Expected to fetch comments for the post."
    except Exception as e:
        pytest.fail(f"Failed to fetch comments for post {post_id}: {str(e)}")
    

@pytest.mark.asyncio
async def test_004_get_reddit_comments_by_date_range_service(session):
    """
    Test to fetch Reddit comments within a specific date range.
    """
    reddit_comments_service = RedditCommentsService(session)
    start_date = "2025-01-01"
    # end date is set to tomorrow to ensure we have comments
    end_date = (date.today() + timedelta(days=1)).isoformat()
    try:
        # load the comments from file
        comments_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_redditComments",
            "test_004_comments_data.json"
        )
        with open(comments_file_path, 'r') as file:
            comments_data = json.load(file)
        # create comments in the database
        reddit_comments = [RedditCommentCreate(**comment) for comment in comments_data]
        await reddit_comments_service.create_reddit_comments_service(reddit_comments)
        # get timestamps for the date range
        start_date_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_date_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        comments = await reddit_comments_service.get_reddit_comments_date_range_service(start_date_timestamp, end_date_timestamp)
        assert isinstance(comments, list), "Expected a list of comments."
        assert all(isinstance(comment, RedditComment) for comment in comments), "Expected all comments to be RedditComment objects."
        assert len(comments) > 0, "Expected at least one comment within the date range."
    except Exception as e:
        pytest.fail(f"Failed to fetch Reddit comments by date range: {str(e)}")
    