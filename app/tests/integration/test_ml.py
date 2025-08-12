from contextlib import asynccontextmanager
import pytest
from app.schemas.ml_models import MLModel, MLModelCreate
from app.schemas.reddit_posts import RedditPostCreate
from app.schemas.reddit_comments import RedditCommentCreate
from app.services.llmService import LLMService
from app.services.cohereService import CohereService
from app.settings.settings import get_settings
from app.services.redditCommentsService import RedditCommentsService
from app.services.redditPostsService import RedditPostsService
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