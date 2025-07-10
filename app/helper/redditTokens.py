from app.models import RedditTokens as RedditTokensModel
from app.schemas.reddit_tokens import RedditToken, RedditTokenCreate
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_reddit_token(session: AsyncSession):
    """
    Fetches the Reddit token from the database.
    """
    try:
        query = select(RedditTokensModel)
        result = await session.execute(query)
        reddit_token = result.scalars().first()

        if not reddit_token:
            return None

        return RedditToken.model_validate(reddit_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Reddit token: {str(e)}; location eaRdb74Fy4")

async def create_reddit_token(session: AsyncSession, reddit_token_create: RedditTokenCreate):
    """
    Creates a new Reddit token in the database.
    """
    try:
        reddit_token = RedditTokensModel(**reddit_token_create.model_dump())
        session.add(reddit_token)
        await session.commit()
        await session.refresh(reddit_token)
        return RedditToken.model_validate(reddit_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating Reddit token: {str(e)}; location bMhXMJz1aY")

async def delete_reddit_token(session: AsyncSession, token_id: int):
    """
    Deletes a Reddit token from the database by its ID.
    """
    try:
        query = select(RedditTokensModel).where(RedditTokensModel.id == token_id)
        result = await session.execute(query)
        reddit_token = result.scalars().first()

        if not reddit_token:
            raise HTTPException(status_code=404, detail="Reddit token not found; location xWw3a1Y9uu")

        await session.delete(reddit_token)
        await session.commit()
        return {"detail": "Reddit token deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting Reddit token: {str(e)}; location bV8g2Cqqpc")