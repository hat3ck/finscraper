
from app.api.dependencies.core import DBSessionDep
from app.helper.redditPosts import get_reddit_posts_user, create_reddit_posts
from app.schemas.reddit_posts import RedditPostCreate
from app.settings.settings import get_settings
import httpx

settings = get_settings()

class RedditPostsService(object):
    def __init__(self, session: DBSessionDep):
        self.session = session
        self.settings = settings
    
    async def get_reddit_posts_user_service(self, author: str):
         # TODO: ADD VALIDATION FOR AUTHOR ID
        reddit_posts = await get_reddit_posts_user(self.session, author)
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
            for subreddit in subreddits:

                posts = await self.get_reddit_posts_from_subreddit(subreddit, posts_per_subreddit, subreddit_sort)
                if not posts:
                    print(f"No posts found for subreddit {subreddit}; location fByiL1JTjd")
                    continue
                print(f"Fetched {len(posts)} posts from subreddit {subreddit}")
                # replace id with post_id to avoid conflicts
                for post in posts:
                    post["post_id"] = post.pop("id")
                reddit_posts = [RedditPostCreate(**post) for post in posts]
                await self.create_reddit_posts_service(reddit_posts)
            await self.session.commit()
            return f"Successfully fetched and saved posts from {len(subreddits)} subreddits ({', '.join(subreddits)})"
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Failed to fetch posts from subreddits: {str(e)}; location UMJGmbCEpr") from e
        
    async def get_reddit_posts_from_subreddit(self, subreddit: str, posts_per_subreddit: int, subreddit_sort: str):
        url = f"https://www.reddit.com/r/{subreddit}/{subreddit_sort}.json?limit={posts_per_subreddit}"
        # send a GET request to the Reddit API
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", {}).get("children", [])
                # make sure the limit is respected
                return [post["data"] for post in posts[:posts_per_subreddit]]
            else:
                raise Exception(f"Failed to fetch posts from subreddit {subreddit}: {response.status_code} - {response.text}; location fByiL1JTjd")