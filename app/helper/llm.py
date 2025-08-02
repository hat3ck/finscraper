from app.models import LlmProviders as LlmProvidersModel
from app.schemas.llm_providers import LLMProvider, LLMProviderCreate
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_active_llm_provider(session: AsyncSession, provider_name: str = None):
    """
    Fetches an active LLM provider by name.
    """
    query = select(LlmProvidersModel).where(
        LlmProvidersModel.is_active.is_(True)
    )
    if provider_name:
        query = query.where(LlmProvidersModel.name == provider_name)
    result = await session.execute(query)
    llm_provider = result.scalars().first()
    
    if not llm_provider:
        raise HTTPException(status_code=404, detail=f"LLM provider '{provider_name}' not found or inactive. location j82NQVBe2")
    
    # convert to schema
    llm_provider = LLMProvider.model_validate(llm_provider)

    return llm_provider

async def create_llm_provider(session: AsyncSession, llm_provider_create: LLMProviderCreate):
    """
    Creates a new LLM provider in the database.
    """
    try:
        llm_provider = LlmProvidersModel(**llm_provider_create.model_dump())
        session.add(llm_provider)
        await session.commit()
        await session.refresh(llm_provider)
        return LLMProvider.model_validate(llm_provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating LLM provider: {str(e)}; location 3O0m2Cqqpc")