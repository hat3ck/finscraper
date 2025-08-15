from app.models import CurrencyPrices as CurrencyPricesModel
from app.schemas.currency_prices import CurrencyPricesCreate, CurrencyPrice
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_currency_prices_from_db(session: AsyncSession) -> list[CurrencyPrice]:
    """
    Fetches currency prices from the database.
    """
    try:
        result = await session.execute(select(CurrencyPricesModel))
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch currency prices from DB: {str(e)} location UmCEerqHdZ") from e
    
async def create_currency_prices(session: AsyncSession, currency_prices: list[CurrencyPricesCreate]) -> list[CurrencyPricesCreate]:
    """
    Creates new currency prices in the database.
    """
    try:
        currency_prices = [CurrencyPricesModel(**price.model_dump()) for price in currency_prices]
        session.add_all(currency_prices)
        await session.commit()
        return currency_prices
    
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create currency prices: {str(e)} location i61KaCX4TM") from e

async def get_currency_prices_by_date_range(session: AsyncSession, start_date: str, end_date: str) -> list[CurrencyPrice]:
    """
    Fetches currency prices within a specific date range.
    """
    try:
        # order 
        query = select(CurrencyPricesModel).where(
            CurrencyPricesModel.timestamp >= start_date,
            CurrencyPricesModel.timestamp <= end_date
        ).order_by(CurrencyPricesModel.timestamp.asc())
        result = await session.execute(query)
        # convert to list of CurrencyPrice schemas
        currency_prices = [CurrencyPrice.model_validate(price) for price in result.scalars().all()]
        return currency_prices
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch currency prices by date range: {str(e)} location iN3h9Lof7H") from e