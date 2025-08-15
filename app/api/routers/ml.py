from app.api.dependencies.core import DBSessionDep
from app.services.mlService import MlService
from fastapi import APIRouter, Query

router = APIRouter(
    prefix="/api/ml",
    tags=["ml"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/predict",
    summary="Create a new prediction for currencies",
    description="Create a new hourly prediction for currencies based on ML models set up for each currency. " \
    "There is an hour_interval parameter to specify the exact hour to predict.",
    response_description="Predictions are being processed in the background.",
)
async def create_prediction(
    session: DBSessionDep,
    hour_interval: int = Query(..., description="Hour interval for the prediction, e.g., 0 for the current hour, 1 for the next hour, etc."),
):
    ml_service = MlService(session)
    result = await ml_service.predict_currencies_sentiment_service(prediction_hour_interval=hour_interval, return_task=False)
    return {"message": result}