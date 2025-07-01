from app.models import RedditPosts as UserRedditPostsModel
from app.schemas.reddit_posts import RedditPost, RedditPostCreate
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


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