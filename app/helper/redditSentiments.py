from app.models import RedditSentiments as RedditSentimentsModel
from app.schemas.reddit_sentiments import RedditSentiment, RedditSentimentsCreate
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

async def create_reddit_sentiments(session: AsyncSession, reddit_sentiments_create: list[RedditSentimentsCreate]):
    """
    Creates new Reddit sentiments in the database.
    """
    try:
        reddit_sentiments = [RedditSentimentsModel(**sentiment.model_dump()) for sentiment in reddit_sentiments_create]
        session.add_all(reddit_sentiments)
        # let the service handle the commit
        return reddit_sentiments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating Reddit sentiments: {str(e)}; location i8HnRCqq2U")