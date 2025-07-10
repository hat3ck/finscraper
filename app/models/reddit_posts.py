from sqlalchemy.orm import Mapped, mapped_column

from . import Base

class RedditPosts(Base):
    __tablename__ = 'reddit_posts'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    post_id: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    subreddit: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)
    score: Mapped[int] = mapped_column(nullable=False)
    num_comments: Mapped[int] = mapped_column(nullable=False)
    created_utc: Mapped[int] = mapped_column(nullable=False)
    selftext: Mapped[str] = mapped_column(nullable=True)
    url: Mapped[str] = mapped_column(nullable=False)