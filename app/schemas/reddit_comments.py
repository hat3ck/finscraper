from pydantic import BaseModel, ConfigDict

class RedditComments(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    post_id: int
    parent_id: int | None = None
    author: str
    body: str
    score: int
    created_utc: int
    depth: int