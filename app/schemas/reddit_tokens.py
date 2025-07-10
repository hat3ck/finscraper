from pydantic import BaseModel, ConfigDict

class RedditToken(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
    expires_in: int
    created_at: int
    token_type: str
    scope: str