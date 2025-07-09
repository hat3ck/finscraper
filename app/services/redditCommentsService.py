
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
        
    async def fetch_comments_from_reddit(self, post_id: str):
        url = f"https://www.reddit.com/comments/{post_id}.json"
        params = {
            "depth": self.settings.comment_depth,
            "limit": self.settings.comments_per_post
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers={"User-Agent": "finscraper"})
            if response.status_code != 200:
                raise Exception(f"Failed to fetch comments from Reddit: {response.text}")
            data = response.json()
            comments = data[1]['data']['children']
            return [comment['data'] for comment in comments if 'data' in comment]
        
    def convert_comments_to_schema(self, post_id: str, comments: list[dict]):
        reddit_comments: list[RedditCommentCreate] = []
        for comment in comments:
            try:
                comment['comment_id'] = comment.pop('id', None)
                comment['post_id'] = post_id
                validated_comment = RedditCommentCreate(**comment)
                reddit_comments.append(validated_comment)
                # get child comments recursively
                child_comments: list[RedditCommentCreate] = []
                self.convert_child_comments_to_schema(post_id, comment, child_comments, current_depth=0)
                reddit_comments.extend(child_comments)
            except:
                pass
        return reddit_comments
    
    def convert_child_comments_to_schema(self, post_id: str, 
                                         comment: dict, 
                                         child_comments: list[RedditCommentCreate]
                                         , current_depth: int):
        if (
        comment.get('replies')
        and isinstance(comment['replies'], dict)
        and 'data' in comment['replies']
        and current_depth < self.settings.comment_depth):
                        children = comment['replies']['data'].get('children', [])
                        for child in children:
                            try:
                                child_data = child.get('data')
                                if not child_data or child_data.get('body') is None:
                                    continue

                                child_data['comment_id'] = child_data.pop('id', None)
                                child_data['post_id'] = post_id
                                validated_child = RedditCommentCreate(**child_data)
                                child_comments.append(validated_child)

                                # recursively fetch deeper comments
                                self.convert_child_comments_to_schema(
                                    post_id, child_data, child_comments, current_depth + 1)
                            except Exception as e:
                                print(f"Error converting child comment: {e}")
                                pass