from typing import Literal
from pydantic import BaseModel, ConfigDict

class WalletsModelBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str | None = None
    currency: str
    platform: str
    address: str
    tag_or_memo: str | None = None
    balance: float
    balance_currency: str
    balance_utilization: float | None = 0.8
    available_balance: float | None = None
    created_utc: int
    updated_utc: int
    is_active: bool = True

class WalletCreate(WalletsModelBase):
    pass

class Wallet(WalletsModelBase):
    id: int