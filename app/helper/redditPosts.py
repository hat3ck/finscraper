from app.models import RedditPosts as UserRedditPostsModel
from app.schemas.reddit_posts import RedditPost, RedditPostCreate
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert


async def get_reddit_posts_user(session: AsyncSession, author: str):
    """
    Fetches all Reddit posts for a given user ID.
    """
    query = select(UserRedditPostsModel).where(UserRedditPostsModel.author == author)
    result = await session.execute(query)
    reddit_posts = result.scalars().all()
    
    if not reddit_posts:
        raise HTTPException(status_code=404, detail="No Reddit posts found for this user; location j6RHyQVBe2")
    
    return reddit_posts

def create_reddit_posts(session: AsyncSession, reddit_posts: list[RedditPostCreate]):
    """
    Creates multiple Reddit posts in the database.
    """
    if not reddit_posts:
        raise HTTPException(status_code=400, detail="No Reddit posts provided; location j6RHyQVBe3")
    
    reddit_posts_models = [UserRedditPostsModel(**post.model_dump()) for post in reddit_posts]
    
    session.add_all(reddit_posts_models)
    
    return reddit_posts_models

async def create_unique_reddit_posts(session: AsyncSession, reddit_posts: list[RedditPostCreate]):
    """
    Inserts Reddit posts only if they do not already exist based on post_id.
    """
    if not reddit_posts:
        raise HTTPException(status_code=400, detail="No Reddit posts provided; location 8hgA74JowE")

    try:
        values = [post.model_dump() for post in reddit_posts]

        stmt = insert(UserRedditPostsModel).values(values)
        stmt = stmt.on_conflict_do_nothing(index_elements=["post_id"])

        await session.execute(stmt)
        
        return values

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred: {str(e)}; location j7NwxTh6hO")
