from app.models.predictions import Predictions as PredictionsModel
from app.schemas.predictions import PredictionsCreate, Prediction
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_predictions_by_currency_date(
    session: AsyncSession,
    currency: str,
    start_date: int,
    end_date: int
) -> list[Prediction]:
    """
    Fetch predictions for a specific currency within a date range.
    """
    try:
        query = select(PredictionsModel).where(
            PredictionsModel.currency == currency,
            PredictionsModel.prediction_timestamp >= start_date,
            PredictionsModel.prediction_timestamp <= end_date
        )
        result = await session.execute(query)
        predictions = result.scalars().all()

        # Convert to Prediction schema
        predictions_converted = [Prediction.model_validate(pred) for pred in predictions]

        if not predictions_converted:
            raise HTTPException(status_code=404, detail=f"No predictions found for currency '{currency}' in the specified date range. location 3khyZTkZXh")

        return predictions_converted
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching predictions: {str(e)}; location xezFJAqFG8") from e
    
async def create_predictions(session: AsyncSession, prediction_create: list[PredictionsCreate]) -> list[Prediction]:
    """
    Creates new predictions in the database.
    """
    try:
        predictions = [PredictionsModel(**pred.model_dump()) for pred in prediction_create]
        session.add_all(predictions)
        # let the caller commit the session
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating predictions: {str(e)}; location 6nK1cgPkG1") from e