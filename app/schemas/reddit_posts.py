from pydantic import BaseModel, ConfigDict

class RedditPostBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
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
