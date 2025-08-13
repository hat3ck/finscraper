from contextlib import asynccontextmanager
import pytest
from app.schemas.currency_prices import CurrencyPricesCreate, CurrencyPrice
from app.services.currencyPricesService import CurrencyPricesService
from app.settings.settings import get_settings
from sqlalchemy import text
from .conftest import table_names
from datetime import datetime
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

@pytest.mark.asyncio
async def test_002_create_currency_prices_service(session):
    """
    Test creating currency prices in the database.
    """
    try:
        currency_ids = ["bitcoin", "ethereum", "dogecoin"]  # Example currency IDs
        currency_service = CurrencyPricesService(session)

        # Create currency prices in the database
        created_prices = await currency_service.create_currency_prices_service(currency_ids)
        
        # Check if the created prices are returned correctly
        assert isinstance(created_prices, list), "Created prices should be a list"
        assert len(created_prices) > 0, "Created prices list should not be empty"
        
        # Validate the structure of the first created price item
        first_created_price = created_prices[0]
        assert isinstance(first_created_price, CurrencyPricesCreate), "First created price item should be a CurrencyPrice instance"
        
    except Exception as e:
        await shutdown_event()
        assert False, f"Unexpected error during creating currency prices: {str(e)}"
    
    await shutdown_event()  # Clean up the database after the test

@pytest.mark.asyncio
async def test_003_get_currency_prices_by_date_range(session):
    """
    Test fetching currency prices by date range.
    """
    try:
        # First, create some currency prices to test with
        currency_service = CurrencyPricesService(session)
        currency_ids = ["btc", "eth", "ada"]
        await currency_service.create_currency_prices_service(currency_ids)
        # start_date will be beginning of 2025 in timestamp format
        start_date = datetime(2025, 1, 1).timestamp()
        # end_date will be now plus 1 day in timestamp format
        end_date = datetime.now().timestamp() + 86400
        # Fetch currency prices by date range
        currency_prices = await currency_service.get_currency_prices_by_date_range_service(
            start_date=start_date,
            end_date=end_date
        )
        
        # Check if the prices are returned correctly
        assert isinstance(currency_prices, list), "Currency prices should be a list"
        assert len(currency_prices) > 0, "Currency prices list should not be empty"
        
    except Exception as e:
        await shutdown_event()
        assert False, f"Failed to set up date range for test: {str(e)}"