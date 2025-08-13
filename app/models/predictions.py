from sqlalchemy.orm import Mapped, mapped_column

from . import Base

class Predictions(Base):
    __tablename__ = 'predictions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    currency: Mapped[str] = mapped_column(nullable=False, index=True)
    priced_in: Mapped[str] = mapped_column(nullable=False, index=True, default='usd')
    currency_price: Mapped[float] = mapped_column(nullable=False)
    model_provider: Mapped[str] = mapped_column(nullable=False, index=True)
    model: Mapped[str] = mapped_column(nullable=False, index=True)
    predicted_price: Mapped[float] = mapped_column(nullable=False)
    prediction_timestamp: Mapped[int] = mapped_column(nullable=False, index=True)
    created_utc: Mapped[int] = mapped_column(nullable=False, index=True)