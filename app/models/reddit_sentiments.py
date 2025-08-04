from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from . import Base

class RedditSentiments(Base):
    __tablename__ = 'reddit_sentiments'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[str] = mapped_column(nullable=False, index=True)
    comment_id: Mapped[str | None] = mapped_column(nullable=False)
    crypto_sentiment: Mapped[str | None] = mapped_column(nullable=False)
    future_sentiment: Mapped[str | None] = mapped_column(nullable=False)
    emotion: Mapped[str | None] = mapped_column(nullable=False)
    subjective: Mapped[str | None] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint('post_id', 'comment_id', name='uq_post_comment'),
    )