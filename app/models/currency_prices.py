from sqlalchemy.orm import Mapped, mapped_column

from . import Base

class CurrencyPrices(Base):
    __tablename__ = 'currency_prices'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    currency: Mapped[str] = mapped_column(nullable=False, index=True)
    price: Mapped[float] = mapped_column(nullable=False)
    price_currency: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[int] = mapped_column(nullable=False)
    source: Mapped[str] = mapped_column(nullable=False)
    market_cap: Mapped[float] = mapped_column(nullable=True)
    total_volume: Mapped[float] = mapped_column(nullable=True)
    total_supply: Mapped[float] = mapped_column(nullable=True)
    ath: Mapped[float] = mapped_column(nullable=True)
    ath_date: Mapped[str] = mapped_column(nullable=True)