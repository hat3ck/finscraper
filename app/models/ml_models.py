from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON
from . import Base

class MlModels(Base):
    __tablename__ = 'ml_models'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    prediction_currency: Mapped[str] = mapped_column(nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(nullable=True)
    provider: Mapped[str] = mapped_column(nullable=False, index=True)
    model: Mapped[str] = mapped_column(nullable=False, index=True)
    model_type: Mapped[str] = mapped_column(nullable=False)
    hyperparameters: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    numeric_features: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    categorical_features: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    target_variable: Mapped[str | None] = mapped_column(nullable=True)
    created_utc: Mapped[int] = mapped_column(nullable=False)
    updated_utc: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)