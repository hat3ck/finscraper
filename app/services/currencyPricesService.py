
from app.api.dependencies.core import DBSessionDep
from app.schemas.currency_prices import CurrencyPricesCreate, CurrencyPrice
from app.settings.settings import get_settings
from app.services.redditTokenService import RedditTokenService
from app.helper.currencyPrices import get_currency_prices_from_db
import httpx
import time

class CurrencyPricesService(object):
    def __init__(self, session: DBSessionDep):
        self.session = session
        self.settings = get_settings()
        self.redditTokenService = RedditTokenService(session)

    async def get_currency_prices_service_from_db(self):
        await get_currency_prices_from_db(self.session)

    async def fetch_currency_prices_from_coingecko(self, currency_ids: list[str] = None):
        try:
            if currency_ids is None or currency_ids == []:
                currency_ids = self.settings.currency_ids
            
            url = f"https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": self.settings.main_currency,
                "symbols": ','.join(currency_ids),
                "order": "market_cap_desc",
                "per_page": len(currency_ids),
            }
            headers = {
                "accept": "application/json",
                "x-cg-demo-api-key": self.settings.coingecko_api_key
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                if not data:
                    raise ValueError("No data returned from CoinGecko API; location BRwbHiJWQc")
                currency_prices = []
                for item in data:
                    try:
                        currency_price = CurrencyPricesCreate(
                            currency = item.get("symbol"),
                            name = item.get("name"),
                            price = item.get("current_price"),
                            price_currency=self.settings.main_currency,
                            timestamp=int(time.time()),
                            source="coingecko",
                            market_cap=item.get("market_cap"),
                            total_volume=item.get("total_volume"),
                            total_supply=item.get("total_supply"),
                            ath=item.get("ath"),
                            ath_date=item.get("ath_date")
                        )
                        currency_prices.append(currency_price)
                    except Exception as e:
                        print(f"Error processing item {item}: {str(e)}; location F3NQKh0r3B")
                        continue
                return currency_prices
        except httpx.HTTPStatusError as e:
            raise ValueError(f"HTTP error occurred while fetching currency prices: {str(e)}; location iFXLH2NKMQ") from e
        except httpx.RequestError as e:
            raise ValueError(f"Request error occurred while fetching currency prices: {str(e)}; location 1XwnWRu6v8") from e
        except Exception as e:
            raise ValueError(f"An error occurred while fetching currency prices: {str(e)}; location tGS2nv0Htu") from e