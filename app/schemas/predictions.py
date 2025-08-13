from typing import Literal
from pydantic import BaseModel, ConfigDict

class PredictionsModelBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    currency: str
    priced_in: str = 'usd'
    currency_price: float
    model_provider: str
    model: str
    predicted_price: float
    prediction_timestamp: int
    created_utc: int

class PredictionsCreate(PredictionsModelBase):
    pass

class Prediction(PredictionsModelBase):
    id: int