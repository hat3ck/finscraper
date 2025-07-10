from pydantic import BaseModel, ConfigDict
from app.schemas.reddit_comments import RedditCommentCreate

class RedditPostBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    post_id: str
    subreddit: str
    author: str
    score: int
    num_comments: int
    created_utc: int
    selftext: str | None = None
    url: str
class RedditPostCreate(RedditPostBase):
    pass  # everything from base, no id
class RedditPost(RedditPostBase):
    id: int  # for GET responses

class RedditPostsAndComments(BaseModel):
    posts: list[RedditPostCreate]
    comments: list[RedditCommentCreate] 