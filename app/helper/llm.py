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
    
async def update_llm_provider(session: AsyncSession, llm_provider_update: LLMProvider):
    """
    Updates an existing LLM provider in the database.
    """
    try:
        query = select(LlmProvidersModel).where(
            LlmProvidersModel.name == llm_provider_update.name,
            LlmProvidersModel.model == llm_provider_update.model
        )
        result = await session.execute(query)
        llm_provider = result.scalars().first()
        if not llm_provider:
            raise HTTPException(status_code=404, detail=f"LLM provider '{llm_provider_update.name}' not found. location 9V0W1Jn2u")
        # Update fields
        for key, value in llm_provider_update.model_dump().items():
            setattr(llm_provider, key, value)
        await session.commit()
        await session.refresh(llm_provider)
        return LLMProvider.model_validate(llm_provider)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating LLM provider: {str(e)}; location hB2sk82Y3Z")
    
async def increment_llm_provider_token_usage(session: AsyncSession, name: str, model: str, tokens: int):
    """
    Increments the token usage for a specific LLM provider.
    """
    try:
        query = select(LlmProvidersModel).where(
            LlmProvidersModel.name == name,
            LlmProvidersModel.model == model
        )
        result = await session.execute(query)
        llm_provider = result.scalars().first()
        if not llm_provider:
            raise HTTPException(status_code=404, detail=f"LLM provider '{name}' not found. location uN5WlH7I8J")
        
        llm_provider.total_used_tokens += tokens
        await session.commit()
        await session.refresh(llm_provider)
        return LLMProvider.model_validate(llm_provider)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error incrementing token usage: {str(e)}; location 9K0Lo95Bvr")