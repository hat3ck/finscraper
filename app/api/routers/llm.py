from app.api.dependencies.core import DBSessionDep
from app.schemas.llm_providers import LLMProviderCreate, LLMProvider
from fastapi import APIRouter, Query
from app.services.llmService import LLMService
router = APIRouter(
    prefix="/api/llm",
    tags=["llm"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/reddit_sentiments_by_date_range",
    summary="Label Reddit sentiments by date range",
    description="Fetches Reddit sentiments by date range and processes them in the background.",
    response_description="Reddit sentiments are being processed in the background.",
)
async def get_reddit_sentiments_by_date_range(
    session: DBSessionDep,
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format."),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format."),
    batch_size: int = Query(..., description="Batch size for processing Reddit sentiments.")
):
    llm_service = LLMService(session)
    result = await llm_service.label_reddit_sentiments_between_dates_service(start_date, end_date, batch_size=batch_size)
    return {"message": result}

@router.get(
    "/reddit_sentiments_hourly",
    summary="Label past X hours Reddit sentiments",
    description="Fetches past X hours Reddit sentiments and processes them in the background.",
    response_description="Reddit sentiments are being processed in the background.",
)
async def get_reddit_sentiments_today(
    session: DBSessionDep,
    batch_size: int = Query(..., description="Batch size for processing Reddit sentiments."),
    hours: int = Query(24, description="Number of hours to look back for today's sentiments.")
):
    llm_service = LLMService(session)
    result = await llm_service.label_reddit_sentiments_today_service(batch_size=batch_size, hours=hours)
    return {"message": result}