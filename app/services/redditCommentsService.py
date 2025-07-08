
from app.api.dependencies.core import DBSessionDep
from app.helper.redditComments import get_reddit_comments_post, create_reddit_comments
from app.schemas.reddit_comments import RedditCommentCreate
from app.settings.settings import get_settings
import httpx

settings = get_settings()

class RedditCommentsService(object):
    def __init__(self, session: DBSessionDep):
        self.session = session
        self.settings = settings
    
    async def get_reddit_comments_post_service(self, post_id: str):
        # TODO: ADD VALIDATION FOR post_id
        reddit_comments = await get_reddit_comments_post(self.session, post_id)
        return reddit_comments
    
    async def create_reddit_comments_service(self, reddit_posts: list[RedditCommentCreate]):
        try:
            created_comments = create_reddit_comments(self.session, reddit_posts)
            await self.session.commit()
            return created_comments
        except Exception as e:
            await self.session.rollback()
            raise e
        
   