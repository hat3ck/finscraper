import pytest
from app.services.redditTokenService import RedditTokenService
from app.settings.settings import get_settings

settings = get_settings()
        

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