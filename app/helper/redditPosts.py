from datetime import datetime
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

async def get_reddit_posts_by_date_range(session: AsyncSession, start_date: str, end_date: str):
    """
    Fetches Reddit posts within a specific date range.
    """
    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail="Start and end dates are required; location dvnTYqf75g")
    
    # convert string dates to datetime objects
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format; use YYYY-MM-DD; location 3UJCbcHgjS")
    
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date; location wqbuSg42ni")
    
    query = select(UserRedditPostsModel).where(
        UserRedditPostsModel.created_utc >= start_date.timestamp(),
        UserRedditPostsModel.created_utc <= end_date.timestamp()
    )
    result = await session.execute(query)
    reddit_posts = result.scalars().all()

    # convert to a list of RedditPost
    if not reddit_posts:
        return []
    reddit_posts = [RedditPost.model_validate(post) for post in reddit_posts]
    if not reddit_posts:
        return []

    return reddit_posts