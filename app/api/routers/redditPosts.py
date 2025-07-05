from app.api.dependencies.core import DBSessionDep
from app.schemas.reddit_posts import RedditPost, RedditPostCreate
from fastapi import APIRouter, Query
from app.services.redditPostsService import get_reddit_posts_user_service, create_reddit_posts_service
from app.services.redditPostsService import get_posts_from_subreddits_service
from app.settings.settings import get_settings

router = APIRouter(
    prefix="/api/reddit_posts",
    tags=["reddit_posts"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/author",
    response_model=RedditPost,
    summary="Get Reddit posts by author ID",
    description="Fetches all Reddit posts for a given author ID.",
    response_description="List of Reddit posts for the specified author ID",
)
async def get_reddit_posts(
    session: DBSessionDep,
    author: str = Query(..., description="Author ID to fetch Reddit posts for")
):
    reddit_posts = await get_reddit_posts_user_service(session, author)
    return reddit_posts

@router.get(
    "/from_reddit",
    summary="Get all Reddit posts from reddit for specified subreddits in the settings",
    description="Fetches all Reddit posts from the reddit server.",
    response_description="List of all Reddit posts from reddit",
)
async def get_posts_from_subreddits(
    session: DBSessionDep,
    subreddits: list[str] = Query(default=None,),
    posts_per_subreddit: int = Query(default=None),
    subreddit_sort: str = Query(default=None)
):
    settings = get_settings()
    if subreddits is None or subreddits == []:
        subreddits = settings.subreddits
    if posts_per_subreddit is None:
        posts_per_subreddit = settings.posts_per_subreddit
    if subreddit_sort is None:
        subreddit_sort = settings.subreddit_sort
    
    return await get_posts_from_subreddits_service(
        session,
        subreddits=subreddits,
        posts_per_subreddit=posts_per_subreddit,
        subreddit_sort=subreddit_sort
    )

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