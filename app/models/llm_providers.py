from sqlalchemy.orm import Mapped, mapped_column

from . import Base

class LlmProviders(Base):
    __tablename__ = 'llm_providers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    model: Mapped[str] = mapped_column(nullable=False, index=True)
    default_api_key: Mapped[str | None] = mapped_column(nullable=True)
    api_url: Mapped[str | None] = mapped_column(nullable=True)
    tokens_per_minute: Mapped[int | None] = mapped_column(nullable=True)
    calls_per_minute: Mapped[int | None] = mapped_column(nullable=True)
    total_used_tokens: Mapped[int | None] = mapped_column(nullable=True, default=0)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[int] = mapped_column(nullable=False)
    access_token: Mapped[str | None] = mapped_column(nullable=True)
    access_token_expiry: Mapped[int | None] = mapped_column(nullable=True)
    access_token_type: Mapped[str | None] = mapped_column(nullable=True)