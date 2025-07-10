
from app.api.dependencies.core import DBSessionDep
from app.schemas.reddit_tokens import RedditTokenCreate
from app.settings.settings import get_settings
from app.helper.redditTokens import get_reddit_token, create_reddit_token, delete_reddit_token
import httpx
import time

class RedditTokenService(object):
    def __init__(self, session: DBSessionDep):
        self.session = session
        self.settings = get_settings()

    async def get_reddit_token(self):
        try:
            reddit_token = await get_reddit_token(self.session)
            if reddit_token:
                if await self.is_token_expired(reddit_token):
                    await delete_reddit_token(self.session, reddit_token.id)
                    self.session.commit()
                else:
                    return reddit_token
            # If no valid token exists, fetch a new one from Reddit
            reddit_token_data = await self.get_reddit_token_from_reddit()
            if reddit_token_data:
                reddit_token_create: RedditTokenCreate = RedditTokenCreate(
                    access_token=reddit_token_data['access_token'],
                    expires_in=reddit_token_data['expires_in'],
                    created_at=int(time.time()),
                    token_type=reddit_token_data['token_type'],
                    scope=reddit_token_data.get('scope', '')
                )
                reddit_token = await create_reddit_token(self.session, reddit_token_create)
                return reddit_token.access_token
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error fetching Reddit token: {str(e)} location ZENfFU44Ry") from e

        
    
    async def get_reddit_token_from_reddit(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://www.reddit.com/api/v1/access_token",
                    data={"grant_type": "client_credentials"},
                    auth=(self.settings.reddit_client_id, self.settings.reddit_client_secret),
                    headers={"User-Agent": self.settings.reddit_user_agent},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"Failed to fetch Reddit token: {e.response.text} location H3s0O9d4kA") from e
    
    async def is_token_expired(self, reddit_token):
        # Compare created_at and expires_in to determine if the token is expired
        current_time = int(time.time())
        return (current_time - reddit_token.created_at) >= reddit_token.expires_in