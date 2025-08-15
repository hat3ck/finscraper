from contextlib import asynccontextmanager
import pytest
from app.schemas.ml_models import MLModel, MLModelCreate
from app.schemas.reddit_posts import RedditPostCreate
from app.schemas.reddit_comments import RedditCommentCreate
from app.schemas.currency_prices import CurrencyPricesCreate
from app.schemas.llm_providers import LLMProviderCreate
from app.schemas.reddit_sentiments import RedditSentimentsCreate
from app.services.llmService import LLMService
from app.services.cohereService import CohereService
from app.settings.settings import get_settings
from app.services.redditCommentsService import RedditCommentsService
from app.services.redditPostsService import RedditPostsService
from app.helper.currencyPrices import create_currency_prices
from app.helper.redditSentiments import create_reddit_sentiments
from app.services.mlService import MlService
from sqlalchemy import text
from .conftest import table_names
import os
import json
import pandas as pd
import time
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
async def test_001_create_ml_model(session):
    try:
        # Load the ML model data from file
        ml_model_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_ml",
            "test_001_ml_models.json"
        )
        with open(ml_model_file_path, 'r') as file:
            ml_model_data = json.load(file)
        
        # Create ML model schema instance
        ml_model_create = MLModelCreate(**ml_model_data)

        # Initialize the ML service
        ml_service = MlService(session)

        # Create the ML model
        created_ml_model = await ml_service.create_ml_model(ml_model_create)

        # Get model from the database to verify creation
        active_ml_model = await ml_service.get_active_ml_model(
            prediction_currency=created_ml_model.prediction_currency,
            provider=created_ml_model.provider,
            model=created_ml_model.model
        )

        # Assert the created model matches the fetched model
        assert active_ml_model == created_ml_model, "Created ML model does not match fetched model."
    except Exception as e:
        await shutdown_event()
        raise AssertionError(f"Failed to create ML model: {str(e)}")
    await shutdown_event()

@pytest.mark.asyncio
async def test_002_prepare_sentiment_data(session):
    try:
        # STEP 1: Prepare the data in the database

        # Read the currency prices CSV file
        currency_prices_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_ml",
            "test_002_currency_prices.csv"
        )
        currency_prices_df = pd.read_csv(currency_prices_file_path, keep_default_na=False)
        # Read provuder data from file
        provider_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_llm",
            "test_002_provider_data.json"
        )
        with open(provider_file_path, 'r') as file:
            provider_data = json.load(file)

        # Read Reddit Sentiments data
        reddit_sentiments_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_ml",
            "test_002_reddit_sentiments.csv"
        )
        reddit_sentiments_df = pd.read_csv(reddit_sentiments_file_path, keep_default_na=False)

        # Read Reddit posts and comments data
        reddit_posts_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_ml",
            "test_002_reddit_posts.csv"
        )
        reddit_posts_df = pd.read_csv(reddit_posts_file_path, keep_default_na=False)

        reddit_comments_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_ml",
            "test_002_reddit_comments.csv"
        )
        reddit_comments_df = pd.read_csv(reddit_comments_file_path, keep_default_na=False)

        # convert to schemas
        currency_prices_create = [CurrencyPricesCreate(**row) for _, row in currency_prices_df.iterrows()]
        provider_data_create = LLMProviderCreate(**provider_data)
        reddit_sentiments_create = [RedditSentimentsCreate(**row) for _, row in reddit_sentiments_df.iterrows()]
        reddit_posts_create = [RedditPostCreate(**post) for _, post in reddit_posts_df.iterrows()]
        reddit_comments_create = [RedditCommentCreate(**comment) for _, comment in reddit_comments_df.iterrows()]

        # Create them in the database
        llm_service = LLMService(session)
        reddit_posts_service = RedditPostsService(session)
        reddit_comments_service = RedditCommentsService(session)

        await create_currency_prices(session, currency_prices_create)
        await llm_service.create_llm_provider(provider_data_create)
        await create_reddit_sentiments(session, reddit_sentiments_create)
        await reddit_posts_service.create_reddit_posts_service(reddit_posts_create)
        await reddit_comments_service.create_reddit_comments_service(reddit_comments_create)

        assert True, "Data prepared successfully in the database."

        # STEP 2: Prepare the sentiment data using the ML service
        ml_service = MlService(session)

        # Define the date range for sentiment data preparation
        start_date = int(pd.to_datetime("2025-01-01").timestamp())
        end_date = int(pd.to_datetime("now").timestamp())

        # Prepare the sentiment data
        prepared_date = await ml_service.prepare_sentiment_data(start_date, end_date)
        
        sentiment_data = prepared_date.train_data
        last_hour_data = prepared_date.last_hour_data

        # Assert that the sentiment data is a DataFrame and not empty
        assert isinstance(sentiment_data, pd.DataFrame), "Sentiment data is not a DataFrame."
        assert not sentiment_data.empty, "Sentiment data is empty."
        # Assert that the DataFrame contains the expected columns
        expected_columns = ['title', 'post_id', 'subreddit', 'author_x', 'score_x',
                            'num_comments', 'created_utc_x', 'selftext', 'url', 'id_x',
                            'parent_id', 'comment_id', 'author_y', 'body', 'score_y',
                            'created_utc_y', 'depth', 'id_y', 'crypto_sentiment',
                            'future_sentiment', 'emotion', 'subjective', 'id',
                            'date_and_hour', 'currency', 'price_now', 'market_cap_now',
                            'total_volume_now', 'total_supply_now', 'ath_now', 'ath_date_now',
                            'future_price', 'market_cap_future', 'total_volume_future', 
                            'total_supply_future', 'ath_future', 'ath_date_future',
                            'hours_since_ath', 'price_diff_percentage']
        for column in expected_columns:
            assert column in sentiment_data.columns, f"Column '{column}' is missing from sentiment data."
        
        # Assert that the DataFrame has the expected number of rows
        assert len(sentiment_data) > 0, "Sentiment data has no rows."

        # Assert that the last hour data is a DataFrame and not empty
        assert isinstance(last_hour_data, pd.DataFrame), "Last hour data is not a DataFrame."
        assert not last_hour_data.empty, "Last hour data is empty."
        # Assert that the last hour data contains the expected columns
        for column in expected_columns:
            assert column in last_hour_data.columns, f"Column '{column}' is missing from last hour data."

    except Exception as e:
        await shutdown_event()
        raise AssertionError(f"Failed to prepare data in ML service: {str(e)}")
    await shutdown_event()

@pytest.mark.asyncio
async def test_003_predict_currency_price(session):
    try:
        # Load the ML model data from file
        ml_model_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_ml",
            "test_003_ml_models.json"
        )
        with open(ml_model_file_path, 'r') as file:
            ml_model_data = json.load(file)

        # load prepared sentiment data
        prepared_data_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_ml",
            "test_003_prepared_sentiment_data.csv"
        )
        prepared_data_df = pd.read_csv(prepared_data_file_path, keep_default_na=False)

        # load last hour data
        last_hour_data_file_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "test_ml",
            "test_003_last_hour_data.csv"
        )
        last_hour_data_df = pd.read_csv(last_hour_data_file_path, keep_default_na=False)
        
        # Create ML model schema instance
        ml_model_create = MLModelCreate(**ml_model_data)

        # Initialize the ML service
        ml_service = MlService(session)
        # Create the ML model
        created_ml_model = await ml_service.create_ml_model(ml_model_create)

        # call the predict_currency_price method
        predicted_price = await ml_service.predict_currency_price(
            prepared_df=prepared_data_df,
            prediction_df=last_hour_data_df,
            currency="eth"
        )
        # Assert that the predicted price is a float
        assert isinstance(predicted_price, float), "Predicted price is not a float."
        assert predicted_price > 0, "Predicted price should be greater than 0."

    except Exception as e:
        await shutdown_event()
        raise AssertionError(f"Failed to load ML model data: {str(e)}")
    await shutdown_event()