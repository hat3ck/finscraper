from app.api.dependencies.core import DBSessionDep
from app.schemas.currency_prices import CurrencyPricesCreate, CurrencyPrice
from fastapi import APIRouter, Query
from app.services.currencyPricesService import CurrencyPricesService
router = APIRouter(
    prefix="/api/currency_prices",
    tags=["currency_prices"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/",
    summary="Get currency prices",
    description="Fetches currency prices from coingecko and saves them to the database.",
    response_description="successfully fetched and saved currency prices",
)
async def get_currency_prices(
    session: DBSessionDep,
    symbols: list[str] = Query(None, description="List of currency symbols to fetch prices for. If not provided, defaults to settings.currency_list.")
):
    currency_prices_service = CurrencyPricesService(session)
    await currency_prices_service.create_currency_prices_service(symbols)
    return {"message": "Successfully fetched and saved currency prices."}