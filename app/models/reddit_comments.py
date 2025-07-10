from sqlalchemy.orm import Mapped, mapped_column

from . import Base

class RedditComments(Base):
    __tablename__ = 'reddit_comments'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[str] = mapped_column(nullable=False, index=True)
    parent_id: Mapped[str | None] = mapped_column(nullable=True)
    comment_id: Mapped[str | None] = mapped_column(nullable=True)
    author: Mapped[str] = mapped_column(nullable=False)
    body: Mapped[str] = mapped_column(nullable=False)
    score: Mapped[int] = mapped_column(nullable=False)
    created_utc: Mapped[int] = mapped_column(nullable=False)
    depth: Mapped[int] = mapped_column(nullable=False)