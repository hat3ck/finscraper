from app.models import RedditSentiments as RedditSentimentsModel
from app.schemas.reddit_sentiments import RedditSentiment, RedditSentimentsCreate
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

async def create_reddit_sentiments(session: AsyncSession, reddit_sentiments_create: list[RedditSentimentsCreate]):
    """
    Creates new Reddit sentiments in the database.
    """
    try:
        reddit_sentiments = [RedditSentimentsModel(**sentiment.model_dump()) for sentiment in reddit_sentiments_create]
        records_to_insert = [sentiment.model_dump() for sentiment in reddit_sentiments_create]
        stmt = insert(RedditSentimentsModel).values(records_to_insert)
        stmt = stmt.on_conflict_do_nothing(index_elements=['post_id', 'comment_id'])
        await session.execute(stmt)
        return reddit_sentiments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating Reddit sentiments: {str(e)}; location i8HnRCO6Pw")