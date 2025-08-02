from io import StringIO
import pandas as pd
from app.services.cohereService import CohereService
from app.settings.settings import get_settings
from app.helper.llm import get_active_llm_provider, create_llm_provider, increment_llm_provider_token_usage
from app.schemas.llm_providers import LLMProvider, LLMProviderCreate


class LLMService(object):
    def __init__(self, session):
        self.session = session
        self.settings = get_settings()
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
        1- crypto_sentiment:(positive, neutral, negative)
        2- future_sentiment: (positive, neutral, negative)
        3- emotion: (happiness, hope, anger, sadness, fear)
        4- subjective: (yes, no)

        Return the full result as a **valid CSV with the same number of rows** and the following columns:

        post_id,comment_id,crypto_sentiment,future_sentiment,emotion,subjective

        Do not skip any rows. Do not add explanations. Only return the CSV content.

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
        if (len(response_df) < min_length):
            print(f"[WARNING] Response has {len(response_df)} rows while {min_length} rows are required")
            print(response_df)
            # Throw Exception
            raise Exception
        return response_df

    async def get_reddit_sentiments_by_date_range(self, start_date: str, end_date: str, batch_size: int = 100):
        # TODO: get posts and comments from Reddit within the date range
        # TODO: Implement a logic to merge them
        # TODO: Call get_sentiments method to get the sentiments
        # TODO: store the results in the database
        raise NotImplementedError("This method is not implemented yet.")