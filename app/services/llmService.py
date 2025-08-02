from app.services.cohereService import CohereService
from app.settings.settings import get_settings
from app.helper.llm import get_active_llm_provider, create_llm_provider
from app.schemas.llm_providers import LLMProvider, LLMProviderCreate


class LLMService(object):
    def __init__(self, session):
        self.session = session
        self.settings = get_settings()
        self.llmProviders = {
            "cohere": CohereService,
            # Add other LLM providers here as needed
            # "openai": OpenAIService,
        }
    
    async def get_active_llm_provider_service(self, provider_name: str = None):
        llm_provider = await get_active_llm_provider(self.session, provider_name)
        return llm_provider
    
    async def create_llm_provider(self, llm_provider_create: LLMProviderCreate):
        """
        Creates a new LLM provider in the database.
        """
        # TODO: Implement validation
        llm_provider = await create_llm_provider(self.session, llm_provider_create)
        return llm_provider