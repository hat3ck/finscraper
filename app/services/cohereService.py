
import cohere
from app.settings.settings import get_settings
from app.schemas.llm_providers import LLMProvider


class CohereService:
    def __init__(self, session):
        self.session = session
        self.settings = get_settings()
    
    async def generate_text(self, prompt: str, llm_provider: LLMProvider):
        """
        Generate text using Cohere's API.
        """
        try:
            token_usage = 0
            if not llm_provider.default_api_key:
                raise ValueError("API key is required for Cohere service. location oW9bCqqpc")
            co = cohere.ClientV2(llm_provider.default_api_key)
            response = co.chat(
                model=llm_provider.model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            response_text = response.message.content[0].text
            token_usage += response.usage.tokens.input_tokens
            token_usage += response.usage.tokens.output_tokens
            # TODO: Add a method to update token usage in the database
            return response_text
        except Exception as e:
            raise ValueError(f"Failed to initialize Cohere client: {str(e)}; location aqNxMwGz2C")
        
