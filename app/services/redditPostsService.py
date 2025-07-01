
from app.api.dependencies.core import DBSessionDep
from app.helper.redditPosts import get_reddit_posts_user, create_reddit_posts
from app.schemas.reddit_posts import RedditPost, RedditPostCreate


async def get_reddit_posts_user_service(session: DBSessionDep, author: str):
    # TODO: ADD VALIDATION FOR AUTHOR ID
    reddit_posts = await get_reddit_posts_user(session, author)
    return reddit_posts

async def create_reddit_posts_service(session: DBSessionDep, reddit_posts: list[RedditPostCreate]):
    # TODO: ADD VALIDATION FOR REDDIT POSTS
    try:
        created_posts = create_reddit_posts(session, reddit_posts)
        await session.commit()
        return reddit_posts
    except Exception as e:
        await session.rollback()
        raise e