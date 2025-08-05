from datetime import datetime, timedelta
from io import StringIO
import pandas as pd
from app.services.cohereService import CohereService
from app.services.redditCommentsService import RedditCommentsService
from app.services.redditPostsService import RedditPostsService
from app.settings.settings import get_settings
from app.helper.llm import get_active_llm_provider, create_llm_provider, increment_llm_provider_token_usage
from app.helper.redditSentiments import create_reddit_sentiments
from app.schemas.llm_providers import LLMProvider, LLMProviderCreate
from app.schemas.reddit_sentiments import RedditSentimentsCreate
import time
import asyncio

class LLMService(object):
    def __init__(self, session):
        self.session = session
        self.settings = get_settings()
        self.reddit_comments_service = RedditCommentsService(session)
        self.reddit_posts_service = RedditPostsService(session)
        cohere_service = CohereService(session)
        self.llmProviders = {
            "cohere": cohere_service,
            # Add other LLM providers here as needed
            # "openai": OpenAIService,
        }
    
    async def get_active_llm_provider_service(self, provider_name: str = None):
        llm_provider = await get_active_llm_provider(self.session, provider_name)
        return llm_provider
    
    async def create_llm_provider(self, llm_provider_create: LLMProviderCreate):
        # TODO: Implement validation
        llm_provider = await create_llm_provider(self.session, llm_provider_create)
        return llm_provider
    
    async def get_sentiments(self, data: pd.DataFrame, llm_provider: LLMProvider):
        prompt_text = f"""The following data (in CSV format) is showing posts and comments related to Crypto subreddit.
        There are 5 fields: 'post_id' and 'comment_id' used for identification. 'title' which indicates the title of the post, 'selftext' which shows publisher's text content, and 'body' indicates the comment text.

        Given these information, provide the following fields in the output:

        1- crypto_sentiment: acceptable values are ["positive", "neutral", "negative"]
        2- future_sentiment: acceptable values are ["positive", "neutral", "negative"]
        3- emotion: acceptable values are ["happiness", "hope", "anger", "sadness", "fear", "neutral"]
        4- subjective: acceptable values are ["yes", "no"]

        Return the full result as a **valid CSV with the same number of rows** and the following columns:

        post_id,comment_id,crypto_sentiment,future_sentiment,emotion,subjective

        Make sure the values for each field are in the exact format as described in the numbered items above. Do not add any extra spaces. Do not skip any rows. Do not add explanations. Only return the CSV content. 

        Data:"""
        data_csv = data.to_csv(index=False)
        prompt = f"{prompt_text}\n{data_csv}"
        try:
            # get active LLM provider
            llm_provider_config = await self.get_active_llm_provider_service(llm_provider.name)
            response = await self.llmProviders[llm_provider.name].generate_text(prompt, llm_provider_config)
            # parse the response into desired format
            response_df = self.parse_sentiments_response(data, response.response_text)
            await increment_llm_provider_token_usage(self.session, llm_provider_config.name,
                                                     llm_provider_config.model,
                                                     response.token_usage)
            return response_df
        except Exception as e:
            raise ValueError(f"Failed to generate sentiments: {str(e)}; location xtY7QkX8gY")
        
    def parse_sentiments_response(self, data_df: pd.DataFrame, response_text: str):
        cleaned_response_text = response_text.replace("\\n", "\n").strip('"')
        # convert to pandas dataframe
        response_df = pd.read_csv(StringIO(cleaned_response_text))
        # Remove space from field names
        response_df.columns = response_df.columns.str.replace(' ', '')
        # Ensure response has at least 90% of the rows
        min_length = (9/10) * len(data_df)
        error_length = (2/10) * len(data_df)
        if (len(response_df) < min_length):
            print(f"[WARNING] Response has {len(response_df)} rows while at least {min_length} rows are required")
            # Do nothing, just throw a warning
        if (len(response_df) > len(data_df) + error_length):
            raise ValueError(f"Response has {len(response_df)} rows while {len(data_df)} rows are expected; location 9V0W1Jn2u")
        # Ensure the combo of post_id and comment_id is unique, otherwise drop duplicates
        response_df.drop_duplicates(subset=['post_id', 'comment_id'], inplace=True)
        return response_df

    async def get_reddit_sentiments_by_date_range(self, start_date: str, end_date: str, batch_size: int, return_task: bool = False):
        
        if not start_date or not end_date:
            raise ValueError("Start date and end date are required. location uNb26Jn2u")
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            # end date will be the end of the day
            end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
            start_date_timestamp = int(start_date.timestamp())
            end_date_timestamp = int(end_date.timestamp())
        except ValueError:
            raise ValueError("Invalid date format; use YYYY-MM-DD; location h82Y6Jo2T")
        # update reddit fetch batch size from settings
        if not batch_size:
            batch_size = self.settings.reddit_fetch_batch_size
        # get active LLM provider
        llm_provider_config = await self.get_active_llm_provider_service()
        # get posts and comments from Reddit within the date range
        posts = await self.reddit_posts_service.get_reddit_posts_by_date_range_service(start_date_timestamp, end_date_timestamp)
        comments = await self.reddit_comments_service.get_reddit_comments_date_range_service(start_date_timestamp, end_date_timestamp)
        if not posts or not comments:
            raise ValueError("No posts or comments found in the specified date range. location uM2wFJn2u")
        # convert posts and comments to DataFrames
        posts_df = pd.DataFrame([post.model_dump() for post in posts])
        comments_df = pd.DataFrame([comment.model_dump() for comment in comments])
        # connect reddit posts and comments using post_id
        reddit_posts_comments = pd.merge(posts_df, comments_df, on='post_id')
        # convert created_utc_x and created_utc_y to dates from timestamp
        reddit_posts_comments['created_utc_x'] = pd.to_datetime(reddit_posts_comments['created_utc_x'], unit='s')
        reddit_posts_comments['created_utc_y'] = pd.to_datetime(reddit_posts_comments['created_utc_y'], unit='s')
        # keep post_id, comment_id, title, selftext, body
        selected_df = reddit_posts_comments[['post_id', 'comment_id', 'title', 'selftext', 'body']].copy()
        # divide the data into parts of batch_size rows for each cohere API call
        selected_dfs = [selected_df[i:i+batch_size] for i in range(0, len(selected_df), batch_size)]
        # Make it a background task due to the long processing time
        task = asyncio.create_task(
            self.get_reddit_sentiments_dataframes(selected_dfs, llm_provider_config)
        )
        if return_task:
            return "Reddit sentiments are being processed in the background.", task
        else:
            return "Reddit sentiments are being processed in the background."

    async def get_reddit_sentiments_dataframes(self, selected_dfs: list[pd.DataFrame], llm_provider: LLMProvider):
        # Call get_sentiments method to get the sentiments
        for part_df in selected_dfs:
            response_df = await self.get_sentiments(part_df, llm_provider)
            # add a delay of rate limit for api requests
            delay = await self.calculate_api_request_delay(llm_provider)
            time.sleep(delay)
            try:
                # save the sentiments to the database
                await self.create_reddit_sentiments(response_df)
                await self.session.commit()
            except Exception as e:
                print(f"Failed to create Reddit sentiments for batch {part_df.index[0]}-{part_df.index[-1]}: {str(e)}; location H7gBbcHpE8")
                print("Skipping this batch and continuing with the next one.")
                await self.session.rollback()
                continue
        print(f"Successfully processed {len(selected_dfs)} batches of Reddit sentiments. location u3nm5J8Bw")
        return "Reddit sentiments were created successfully."

    async def create_reddit_sentiments(self, sentiments_df: pd.DataFrame):
        reddit_sentiments = []
        for _, row in sentiments_df.iterrows():
            try:
                reddit_sentiment = RedditSentimentsCreate(
                    post_id=row['post_id'],
                    comment_id=row['comment_id'],
                    crypto_sentiment=row['crypto_sentiment'],
                    future_sentiment=row['future_sentiment'],
                    emotion=row['emotion'],
                    subjective=row['subjective']
                )
                reddit_sentiments.append(reddit_sentiment)
            except Exception as e:
                print(f"Failed to create Reddit sentiment for row {row['post_id']}, {row['comment_id']}: {str(e)}; location I3NeT6BfOy")
                continue
        # Save to database
        await create_reddit_sentiments(self.session, reddit_sentiments)
        return reddit_sentiments
    
    async def calculate_api_request_delay(self, llm_provider: LLMProvider):
        """
        Calculate the delay based on the LLM provider's rate limits.
        """
        if llm_provider.calls_per_minute:
            requests_per_minute = llm_provider.calls_per_minute
            if requests_per_minute > 0:
                delay = 60 / requests_per_minute
                # add a small buffer to avoid hitting the limit
                return delay + 0.9
        return 0.1