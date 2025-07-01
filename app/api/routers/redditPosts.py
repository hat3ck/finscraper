from app.api.dependencies.core import DBSessionDep
from app.schemas.reddit_posts import RedditPost, RedditPostCreate
from fastapi import APIRouter
from app.services.redditPostsService import get_reddit_posts_user_service, create_reddit_posts_service

router = APIRouter(
    prefix="/api/reddit_posts",
    tags=["reddit_posts"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/{author}",
    response_model=RedditPost,
    summary="Get Reddit posts by author ID",
    description="Fetches all Reddit posts for a given author ID.",
    response_description="List of Reddit posts for the specified author ID",
)
async def get_reddit_posts(
    author: str,
    session: DBSessionDep
):
    reddit_posts = await get_reddit_posts_user_service(session, author)
    return reddit_posts

@router.post(
    "/",
    response_model=list[RedditPostCreate],
    summary="Create Reddit posts",
    description="Creates new Reddit posts in the database.",
    response_description="List of created Reddit posts",
)
async def create_reddit_posts(
    reddit_posts: list[RedditPostCreate],
    session: DBSessionDep
):
    created_posts = await create_reddit_posts_service(session, reddit_posts)
    return created_posts