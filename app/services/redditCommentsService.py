
from app.api.dependencies.core import DBSessionDep
from app.helper.redditComments import get_reddit_comments_post, create_reddit_comments, get_reddit_comments_by_date_range
from app.schemas.reddit_comments import RedditCommentCreate
from app.settings.settings import get_settings
import httpx
from app.services.redditTokenService import RedditTokenService

settings = get_settings()

class RedditCommentsService(object):
    def __init__(self, session: DBSessionDep):
        self.session = session
        self.settings = settings
        self.redditTokenService = RedditTokenService(session)
    
    async def get_reddit_comments_post_service(self, post_id: str):
        # TODO: ADD VALIDATION FOR post_id
        reddit_comments = await get_reddit_comments_post(self.session, post_id)
        return reddit_comments

    async def get_reddit_comments_date_range_service(self, start_date_timestamp: int, end_date_timestamp: int):
        reddit_comments = await get_reddit_comments_by_date_range(self.session, start_date_timestamp, end_date_timestamp)
        return reddit_comments
    
    async def create_reddit_comments_service(self, reddit_comments: list[RedditCommentCreate]):
        try:
            created_comments = create_reddit_comments(self.session, reddit_comments)
            await self.session.commit()
            return created_comments
        except Exception as e:
            await self.session.rollback()
            raise e
        
    async def fetch_comments_from_reddit_service(self, post_id: str, sort: str = "top"):
        """
        Fetches comments for a specific Reddit post.
        """
        try:
            if not post_id:
                raise ValueError("Post ID must be provided; location JcQQHM85gL")
            if sort not in ["top", "new", "old", "controversial"]:
                raise ValueError(f"Invalid sort option: {sort}; location ei0QyQYXxS")
            if sort is None:
                sort = self.settings.comment_sort
            
            comments = await self.fetch_comments_from_reddit(post_id, sort)
            if not comments:
                print(f"No comments found for post {post_id}; location X1HfZvbBdQ")
                return []
            
            reddit_comments = self.convert_comments_to_schema(post_id, comments)
            await self.create_reddit_comments_service(reddit_comments)
            return reddit_comments
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Failed to fetch comments for post {post_id}: {str(e)}; location Zqrn2pdH7J") from e
         
        
    async def fetch_comments_from_reddit(self, post_id: str, sort: str = "top"):
        url = f"https://oauth.reddit.com/comments/{post_id}.json"
        access_token = await self.redditTokenService.get_reddit_token()
        params = {
            "depth": self.settings.comment_depth,
            "limit": self.settings.comments_per_post,
            "sort": sort
        }
        headers = {
            "User-Agent": self.settings.reddit_user_agent,
            "Authorization": f"Bearer {access_token}"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
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