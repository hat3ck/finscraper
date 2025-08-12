from sqlalchemy.orm import Mapped, mapped_column

from . import Base

class Wallets(Base):
    __tablename__ = 'wallets'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(nullable=True)
    currency: Mapped[str] = mapped_column(nullable=False, index=True)
    platform: Mapped[str] = mapped_column(nullable=False, index=True)
    address: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    tag_or_memo: Mapped[str | None] = mapped_column(nullable=True)
    balance: Mapped[float] = mapped_column(nullable=False)
    balance_currency: Mapped[str] = mapped_column(nullable=False)
    balance_utilization: Mapped[float | None] = mapped_column(nullable=True, default=0.8)
    available_balance: Mapped[float | None] = mapped_column(nullable=True)
    created_utc: Mapped[int] = mapped_column(nullable=False)
    updated_utc: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)