from pydantic import BaseModel, ConfigDict

class LLMProviderBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    model: str
    default_api_key: str | None = None
    api_url: str | None = None
    tokens_per_minute: int | None = None
    calls_per_minute: int | None = None
    total_used_tokens: int | None = 0
    is_active: bool = True
    created_at: int
    access_token: str | None = None
    access_token_expiry: int | None = None
    access_token_type: str | None = None

class LLMProviderCreate(LLMProviderBase):
    pass  # everything from base, no id

class LLMProvider(LLMProviderBase):
    id: int  # for GET responses

class GenerateTextResponse(BaseModel):
    response_text: str
    token_usage: int