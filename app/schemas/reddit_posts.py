from pydantic import BaseModel, ConfigDict

class RedditPost(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    subreddit: str
    author: str
    score: int
    num_comments: int
    created_utc: int
    selftext: str | None = None
    url: str