import pytest
from app.schemas.llm_providers import LLMProvider, LLMProviderCreate
from app.schemas.reddit_posts import RedditPostCreate
from app.schemas.reddit_comments import RedditCommentCreate
from app.services.llmService import LLMService
from app.services.cohereService import CohereService
from app.settings.settings import get_settings
from app.services.redditCommentsService import RedditCommentsService
from app.services.redditPostsService import RedditPostsService
from sqlalchemy import text
import os
import json
import pandas as pd

settings = get_settings()
        
@pytest.mark.asyncio
async def test_000():
    """
    Test to ensure the test suite is running.
    """
    assert True, "Test suite is running correctly."

@pytest.mark.asyncio
async def test_001_get_llm_provider(session):
    """
    Test to fetch an active LLM provider.
    """
    llm_provider_service = LLMService(session)
    try:
        # load the provider from file under tests/integration/data/test_llm/test_001_provider_data.json
        provider_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_llm",
            "test_001_provider_data.json"
        )
        with open(provider_file_path, 'r') as file:
            provider_data = json.load(file)
        
        # convert to schema
        provider_data = LLMProviderCreate(**provider_data)
        # replace the default_api_key with the one from the .env file
        provider_data.default_api_key = os.getenv("COHERE_API_KEY")
        # create the provider in the database
        await llm_provider_service.create_llm_provider(provider_data)
        # fetch the provider config from the database
        llm_provider = await llm_provider_service.get_active_llm_provider_service()
        assert llm_provider, "LLM provider should be fetched successfully."
        assert llm_provider.name == provider_data.name, "LLM provider name should match the created provider."
    except Exception as e:
        pytest.fail(f"Failed to fetch LLM provider: {str(e)}")

@pytest.mark.asyncio
async def test_002_generate_text_with_cohere(session):
        """
        Test to generate text using Cohere's API.
        """
        cohere_service = CohereService(session)
        try:
            # load the provider from file under tests/integration/data/test_llm/test_001_provider_data.json
            provider_file_path = os.path.join(
                os.path.dirname(__file__),
                "data",
                "test_llm",
                "test_002_provider_data.json"
            )
            with open(provider_file_path, 'r') as file:
                provider_data = json.load(file)
            
            # convert to schema
            provider_data = LLMProvider(**provider_data)
            # replace the default_api_key with the one from the .env file
            provider_data.default_api_key = os.getenv("COHERE_API_KEY")
            
            prompt = "What is the capital of France?"
            response = await cohere_service.generate_text(prompt, provider_data)
            response_text = response.response_text
            token_usage = response.token_usage
            assert token_usage > 0, "Token usage should be greater than 0."
            assert response_text, "Response text should not be empty."
            assert isinstance(response_text, str), "Response text should be a string."
            assert "paris" in response_text.lower(), "Response text should contain 'paris'."
            
        except Exception as e:
            pytest.fail(f"Failed to generate text with Cohere: {str(e)}")

@pytest.mark.asyncio
async def test_003_get_sentiments(session):
    """
    Test to get sentiments using the LLMService.
    """
    llm_service = LLMService(session)
    try:
        # load the provider from file under tests/integration/data/test_llm/test_001_provider_data.json
        provider_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_llm",
            "test_003_provider_data.json"
        )
        with open(provider_file_path, 'r') as file:
            provider_data = json.load(file)

        # load the dataframe from file under tests/integration/data/test_llm/test_003_input_data.csv
        data_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_llm",
            "test_003_input_data.csv"
        )
        data = pd.read_csv(data_file_path)
        if data.empty:
            pytest.skip("Input data is empty, skipping test.")
        
        # replace the default_api_key with the one from the .env file
        provider_data['default_api_key'] = os.getenv("COHERE_API_KEY")

        # create the provider in the database
        provider_data_create = LLMProviderCreate(**provider_data)
        await llm_service.create_llm_provider(provider_data_create)

        # convert to schema
        provider_data = LLMProvider(**provider_data)

        # replace the default_api_key with the one from the .env file
        provider_data.default_api_key = os.getenv("COHERE_API_KEY")
        
        response = await llm_service.get_sentiments(data, provider_data)
        assert isinstance(response, pd.DataFrame), "Response should be a pandas DataFrame."
        assert not response.empty, "Response DataFrame should not be empty."
        assert set(response.columns) == {'post_id', 'comment_id', 'crypto_sentiment', 'future_sentiment', 'emotion', 'subjective'}, "Response DataFrame should have the correct columns."
        assert len(response) == len(data), "Response DataFrame should have the same number of rows as input data."

    except Exception as e:
        pytest.fail(f"Failed to get sentiments: {str(e)}")

@pytest.mark.asyncio()
async def test_004_create_reddit_sentiments(session):
    """
    Test to create Reddit sentiments in the database.
    """
    llm_service = LLMService(session)
    reddit_posts_service = RedditPostsService(session)
    reddit_comments_service = RedditCommentsService(session)
    try:
        # load the provider from file under tests/integration/data/test_llm/test_001_provider_data.json
        provider_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_llm",
            "test_004_provider_data.json"
        )
        with open(provider_file_path, 'r') as file:
            provider_data = json.load(file)

        # load reddit_posts and reddit_comments from files
        reddit_posts_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_llm",
            "test_004_reddit_posts.csv"
        )
        reddit_comments_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_llm",
            "test_004_reddit_comments.csv"
        )
        reddit_posts = pd.read_csv(reddit_posts_file_path, keep_default_na=False)
        reddit_comments = pd.read_csv(reddit_comments_file_path, keep_default_na=False)
        # replace the default_api_key with the one from the .env file
        provider_data['default_api_key'] = os.getenv("COHERE_API_KEY")
        # create the provider in the database
        provider_data_create = LLMProviderCreate(**provider_data)
        await llm_service.create_llm_provider(provider_data_create)
        # convert to schema
        provider_data = LLMProvider(**provider_data)
        # convert the posts and comments to the appropriate schemas
        reddit_posts_create = [RedditPostCreate(**post) for _, post in reddit_posts.iterrows()]
        reddit_comments_create = [RedditCommentCreate(**comment) for _, comment in reddit_comments.iterrows()]
        # create the posts and comments in the database
        await reddit_posts_service.create_reddit_posts_service(reddit_posts_create)
        await reddit_comments_service.create_reddit_comments_service(reddit_comments_create)

        start_date = "2025-01-01"
        end_date = "2026-01-01"
        
        # get Reddit sentiments by date range
        result, task = await llm_service.label_reddit_sentiments_between_dates_service(start_date, end_date, batch_size=10, return_task=True)
        assert result == "Reddit sentiments are being processed in the background.", "Result message should indicate processing in the background."
        
        # Wait for background task to complete
        await task
        
        # Check if Reddit sentiments were created in the database
        query = text("SELECT COUNT(*) FROM reddit_sentiments")
        result = await session.execute(query)
        count = result.scalar()
        assert count > 0, "Reddit sentiments should be created in the database."

    except Exception as e:
        pytest.fail(f"Failed to prepare data for Reddit sentiments: {str(e)}")
