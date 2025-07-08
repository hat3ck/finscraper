from pydantic import BaseModel, ConfigDict

class RedditComments(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    post_id: str
    parent_id: str | None = None
    comment_id: str | None = None
    author: str
    body: str
    score: int
    created_utc: int
    depth: int