from app.api.dependencies.core import DBSessionDep
from app.schemas.reddit_comments import RedditComment, RedditCommentCreate
from fastapi import APIRouter, Query
from app.services.redditCommentsService import RedditCommentsService
from app.settings.settings import get_settings

router = APIRouter(
    prefix="/api/reddit_comments",
    tags=["reddit_comments"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/post",
    response_model=RedditComment,
    summary="Get Reddit comments for a specific post",
    description="Fetches Reddit comments for a specific post ID.",
    response_description="List of Reddit comments for the specified post ID",
)
async def get_reddit_posts(
    session: DBSessionDep,
    post_id: str = Query(..., description="The ID of the Reddit post to fetch comments for.")
):
    reddit_comments_service = RedditCommentsService(session)
    reddit_comments = await reddit_comments_service.get_reddit_comments_post_service(post_id)
    return reddit_comments

@router.post(
    "/",
    response_model=list[RedditCommentCreate],
    summary="Create Reddit comments",
    description="Creates Reddit comments in the database.",
)
async def create_reddit_comments(
    session: DBSessionDep,
    reddit_comments: list[RedditCommentCreate]
):
    reddit_comments_service = RedditCommentsService(session)
    created_comments = await reddit_comments_service.create_reddit_comments_service(reddit_comments)
    return created_comments