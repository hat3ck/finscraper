from typing import Literal
from pydantic import BaseModel, ConfigDict

class MLModelBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    prediction_currency: str | None = None
    description: str | None = None
    provider: str
    model: str
    model_type: Literal['classification', 'regression', 'clustering', 'neural_network']
    hyperparameters: dict | None = None
    numeric_features: list[str] | None = None
    categorical_features: list[str] | None = None
    target_variable: str | None = None
    created_utc: int
    updated_utc: int
    is_active: bool = True

class MLModelCreate(MLModelBase):
    pass

class MLModel(MLModelBase):
    id: int