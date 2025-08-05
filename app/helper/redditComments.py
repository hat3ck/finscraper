from app.models import RedditComments as UserRedditCommentsModel
from app.schemas.reddit_comments import RedditComment, RedditCommentCreate
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta


async def get_reddit_comments_post(session: AsyncSession, post_id: str):
    """
    Fetches comments for a specific Reddit post.
    """
    if not post_id:
        raise HTTPException(status_code=400, detail="Post ID is required; location twZzmJYtFJ")

    query = select(UserRedditCommentsModel).where(UserRedditCommentsModel.post_id == post_id)
    result = await session.execute(query)
    reddit_comments = result.scalars().all()

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

async def get_reddit_comments_by_date_range(session: AsyncSession, start_date: str, end_date: str):
    """
    Fetches Reddit comments within a specific date range.
    """
    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail="Start and end dates are required; location H8NuLTYVBJ")
    
    # convert string dates to datetime objects
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        # end date will be the end of the day
        end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format; use YYYY-MM-DD; location PtDRch1fe0")
    
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date; location fhgCw4Pvmg")
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="End date cannot be before start date; location CXNZUK6hXw")

    query = select(UserRedditCommentsModel).where(
        UserRedditCommentsModel.created_utc >= start_date.timestamp(),
        UserRedditCommentsModel.created_utc <= end_date.timestamp()
    )
    result = await session.execute(query)
    reddit_comments = result.scalars().all()

    # convert to a list of RedditComment
    if not reddit_comments:
        return []
    reddit_comments = [RedditComment.model_validate(comment) for comment in reddit_comments]
    if not reddit_comments:
        return []
    
    return reddit_comments