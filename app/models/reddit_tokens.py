from sqlalchemy.orm import Mapped, mapped_column

from . import Base

class RedditTokens(Base):
    __tablename__ = 'reddit_tokens'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    access_token: Mapped[str] = mapped_column(nullable=False, unique=True)
    expires_in: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[int] = mapped_column(nullable=False)
    token_type: Mapped[str] = mapped_column(nullable=False)
    scope: Mapped[str] = mapped_column(nullable=False)