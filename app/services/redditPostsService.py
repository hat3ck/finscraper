
import asyncio
from app.api.dependencies.core import DBSessionDep
from app.helper.redditPosts import get_reddit_posts_user, create_reddit_posts, create_unique_reddit_posts
from app.helper.redditPosts import get_reddit_posts_by_date_range
from app.schemas.reddit_posts import RedditPostCreate, RedditPostsAndComments
from app.settings.settings import get_settings
import httpx
from app.services.redditCommentsService import RedditCommentsService
from app.services.redditTokenService import RedditTokenService
import time

settings = get_settings()

class RedditPostsService(object):
    def __init__(self, session: DBSessionDep):
        self.session = session
        self.settings = settings
        self.redditTokenService = RedditTokenService(session)
    
    async def get_reddit_posts_user_service(self, author: str):
         # TODO: ADD VALIDATION FOR AUTHOR ID
        reddit_posts = await get_reddit_posts_user(self.session, author)
        return reddit_posts
    
    async def get_reddit_posts_by_date_range_service(self, start_date: str, end_date: str):
        reddit_posts = await get_reddit_posts_by_date_range(self.session, start_date, end_date)
        return reddit_posts

    async def create_reddit_posts_service(self, reddit_posts: list[RedditPostCreate]):
        # TODO: ADD VALIDATION FOR REDDIT POSTS
        try:
            created_posts = create_reddit_posts(self.session, reddit_posts)
            await self.session.commit()
            return reddit_posts
        except Exception as e:
            await self.session.rollback()
            raise e
    
    async def fetch_posts_and_comments_from_reddit_service(self, 
                                                           subreddits: list[str] = None,
                                                           posts_per_subreddit: int = None,
                                                           comments_per_post: int = None,
                                                           subreddit_sort: str = "top",
                                                           comment_sort: str = "top"):
        try:
            # TODO: ADD VALIDATION 
            if subreddit_sort not in ["top", "new", "hot", "rising"]:
                raise ValueError(f"Invalid post sort option: {subreddit_sort}; location 7JrGg6ATEr")
            if comment_sort not in ["top", "new", "old", "controversial"]:
                raise ValueError(f"Invalid comment sort option: {comment_sort}; location iXwV5kwdRP")
            
            # Fetch posts from configured subreddits
            if subreddits is None or subreddits == []:
                subreddits = self.settings.subreddits
            if posts_per_subreddit is None:
                posts_per_subreddit = self.settings.posts_per_subreddit
            if comments_per_post is None:
                comments_per_post = self.settings.comments_per_post
            if subreddit_sort is None:
                subreddit_sort = self.settings.subreddit_sort
            reddit_posts: list[RedditPostCreate] = await self.get_posts_from_subreddits_service(
                subreddits=subreddits,
                posts_per_subreddit=posts_per_subreddit,
                subreddit_sort=subreddit_sort
            )
            reddit_comments_service = RedditCommentsService(self.session)
            # Fetch comments for each post
            all_comments: list[RedditPostCreate] = []
            for post in reddit_posts:
                try:
                    post_id = post.post_id
                    # from database post_id has comments, do not fetch comments again
                    existing_comments = await reddit_comments_service.get_reddit_comments_post_service(post_id)
                    if existing_comments:
                        print(f"Comments already exist for post {post_id}, skipping fetch; location u2bsHTra7k")
                        continue
                    comments = await reddit_comments_service.fetch_comments_from_reddit_service(post_id, comment_sort)
                    all_comments.extend(comments)
                    print(f"Fetched {len(comments)} comments for post {post_id}")
                except Exception as e:
                    print(f"Failed to fetch comments for post {post.post_id}: {str(e)}; location 0kgrYTra7k")
                    continue
            posts_and_comments = RedditPostsAndComments(
                posts=reddit_posts,
                comments=all_comments
            )
            return posts_and_comments
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Failed to fetch posts and comments from Reddit: {str(e)}; location HqE4RTwQR9") from e

    async def get_posts_from_subreddits_service(self, subreddits: list[str], posts_per_subreddit: int, subreddit_sort: str):
        """
        Fetches posts from specified subreddits.
        """
        try:
            # TODO: MOVE VALIADATIONS TO A SEPARATE FUNCTION
            if not subreddits:
                raise ValueError("No subreddits provided; location fByiL1JTjd")
            if posts_per_subreddit <= 0:
                raise ValueError("Posts per subreddit must be greater than 0; location fByiL1JTjd")
            if subreddit_sort not in ["hot", "new", "top", "rising"]:
                raise ValueError(f"Invalid subreddit sort option: {subreddit_sort}; location fByiL1JTjd")
            all_posts: list[RedditPostCreate] = []
            for subreddit in subreddits:
                reddit_posts: list[RedditPostCreate] = []
                posts = await self.get_reddit_posts_from_subreddit(subreddit, posts_per_subreddit, subreddit_sort)
                if not posts:
                    print(f"No posts found for subreddit {subreddit}; location fByiL1JTjd")
                    continue
                print(f"Fetched {len(posts)} posts from subreddit {subreddit}")
                for post in posts:
                    try:
                        # replace id with post_id to avoid conflicts
                        post["post_id"] = post.pop("id")
                        reddit_posts.append(RedditPostCreate(**post))
                    except:
                        continue
                all_posts.extend(reddit_posts)
                await create_unique_reddit_posts(self.session, reddit_posts)
                await self.session.commit()
            return all_posts
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Failed to fetch posts from subreddits: {str(e)}; location UMJGmbCEpr") from e
        
    async def get_reddit_posts_from_subreddit(self, subreddit: str, posts_per_subreddit: int, subreddit_sort: str):
        url = f"https://oauth.reddit.com/r/{subreddit}/{subreddit_sort}.json?limit={posts_per_subreddit}"
        access_token = await self.redditTokenService.get_reddit_token()
        headers = {
            "User-Agent": settings.reddit_user_agent,
            "Authorization": f"Bearer {access_token}"
        }
        # send a GET request to the Reddit API
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", {}).get("children", [])
                # make sure the limit is respected
                return [post["data"] for post in posts[:posts_per_subreddit]]
            else:
                raise Exception(f"Failed to fetch posts from subreddit {subreddit}: {response.status_code} - {response.text}; location fByiL1JTjd")