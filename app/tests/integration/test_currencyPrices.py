from contextlib import asynccontextmanager
import pytest
from app.schemas.currency_prices import CurrencyPricesCreate, CurrencyPrice
from app.services.currencyPricesService import CurrencyPricesService
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
async def test_001_get_currency_prices_from_coingecko(session):
    """
    Test fetching currency prices from CoinGecko.
    """
    try:
        currency_ids = ["bitcoin", "ethereum", "dogecoin"]  # Example currency IDs
        currency_service = CurrencyPricesService(session)
        prices = await currency_service.fetch_currency_prices_from_coingecko(currency_ids)
        
        # Check if the prices are returned correctly
        assert isinstance(prices, list), "Prices should be a list"
        assert len(prices) > 0, "Prices list should not be empty"
        
        # Validate the structure of the first price item
        first_price = prices[0]
        assert isinstance(first_price, CurrencyPricesCreate), "First price item should be a CurrencyPricesCreate instance"
        
    except Exception as e:
        assert False, f"Unexpected error during fetching currency prices: {str(e)}"