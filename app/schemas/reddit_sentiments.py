from typing import Literal
from pydantic import BaseModel, ConfigDict

class RedditSentimentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    post_id: str
    comment_id: str
    crypto_sentiment: Literal['negative', 'neutral', 'positive'] | None = None
    future_sentiment: Literal['negative', 'neutral', 'positive'] | None = None
    emotion: Literal['happiness', 'hope', 'anger', 'sadness', 'fear', 'neutral'] | None = None
    subjective: Literal['yes', 'no'] | None = None



class RedditSentimentsCreate(RedditSentimentBase):
    pass  # everything from base, no id

class RedditSentiment(RedditSentimentBase):
    id: int  # for GET responses