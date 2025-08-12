from typing import Literal
from pydantic import BaseModel, ConfigDict

class OrdersModelBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    currency: str
    platform: str
    order_currency: str
    ordered_price: float
    ordered_quantity: float
    projected_price: float
    ordered_at: int
    sold_at: int | None = None
    sold_price: float | None = None
    profit_loss: float | None = None
    status: Literal['open', 'closed']

class OrderCreate(OrdersModelBase):
    pass

class Order(OrdersModelBase):
    id: int