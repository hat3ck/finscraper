from sqlalchemy.orm import Mapped, mapped_column

from . import Base

class Orders(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    currency: Mapped[str] = mapped_column(nullable=False, index=True)
    platform: Mapped[str] = mapped_column(nullable=False, index=True)
    order_currency: Mapped[str] = mapped_column(nullable=False, index=True)
    ordered_price: Mapped[float] = mapped_column(nullable=False)
    ordered_quantity: Mapped[float] = mapped_column(nullable=False)
    projected_price: Mapped[float] = mapped_column(nullable=False)
    ordered_at: Mapped[int] = mapped_column(nullable=False)
    sold_at: Mapped[int | None] = mapped_column(nullable=True)
    sold_price: Mapped[float | None] = mapped_column(nullable=True)
    profit_loss: Mapped[float | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, index=True)