from app.models import RedditComments as UserRedditCommentsModel
from app.schemas.reddit_comments import RedditCommentCreate
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_reddit_comments_post(session: AsyncSession, post_id: str):
    """
    Fetches comments for a specific Reddit post.
    """
    if not post_id:
        raise HTTPException(status_code=400, detail="Post ID is required; location twZzmJYtFJ")

    query = select(UserRedditCommentsModel).where(UserRedditCommentsModel.post_id == post_id)
    result = await session.execute(query)
    reddit_comments = result.scalars().all()

    if not reddit_comments:
        raise HTTPException(status_code=404, detail=f"No comments found for post ID {post_id}; location Vyy959uUyu")

    return reddit_comments

def create_reddit_comments(session: AsyncSession, reddit_comments: list[RedditCommentCreate]):
    """
    Creates multiple Reddit comments in the database.
    """
    if not reddit_comments:
        raise HTTPException(status_code=400, detail="No Reddit comments provided; location rndZiwu4Up")

    reddit_comments_models = [UserRedditCommentsModel(**comment.model_dump()) for comment in reddit_comments]

    session.add_all(reddit_comments_models)

    return reddit_comments_models