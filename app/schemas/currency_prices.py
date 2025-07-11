from pydantic import BaseModel, ConfigDict

class CurrencyPricesBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    currency: str
    name: str
    price: float
    price_currency: str
    timestamp: int
    source: str
    market_cap: float | None = None
    total_volume: float | None = None
    total_supply: float | None = None
    ath: float | None = None
    ath_date: str | None = None

class CurrencyPricesCreate(CurrencyPricesBase):
    pass

class CurrencyPrice(CurrencyPricesBase):
    id: int