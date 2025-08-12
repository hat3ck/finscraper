from app.models import MlModels as MlModelsModel
from app.schemas.ml_models import MLModel, MLModelCreate
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_active_ml_model(session: AsyncSession,
                              prediction_currency: str = None,
                              provider: str = None,
                              model: str = None):
    """
    Fetches an active ML model by name.
    """
    query = select(MlModelsModel).where(
        MlModelsModel.is_active.is_(True)
    )
    if provider:
        query = query.where(MlModelsModel.provider == provider)
    if model:
        query = query.where(MlModelsModel.model == model)
    if prediction_currency:
        query = query.where(MlModelsModel.prediction_currency == prediction_currency)
    result = await session.execute(query)
    ml_model = result.scalars().first()

    if not ml_model:
        raise HTTPException(status_code=404, detail=f"ML model '{model}' not found or inactive. location jd8nc7RmS")

    # convert to schema
    ml_model = MLModel.model_validate(ml_model)

    return ml_model

async def create_ml_model(session: AsyncSession, ml_model_create: MLModelCreate):
    """
    Creates a new ML model in the database.
    """
    try:
        ml_model = MlModelsModel(**ml_model_create.model_dump())
        session.add(ml_model)
        await session.commit()
        await session.refresh(ml_model)
        return MLModel.model_validate(ml_model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ML model: {str(e)}; location 8Sb5CjBrZ")