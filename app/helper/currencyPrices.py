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