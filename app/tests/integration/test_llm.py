from contextlib import asynccontextmanager
import pytest
from app.schemas.llm_providers import LLMProvider, LLMProviderCreate
from app.services.llmService import LLMService
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
    await shutdown_event()