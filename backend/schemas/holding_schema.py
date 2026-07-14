from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HoldingBase(BaseModel):
    symbol: str = Field(min_length=1, max_length=40)
    quantity: Decimal = Field(gt=0)
    average_price: Decimal = Field(ge=0)
    exchange: str = Field(default="NSE", min_length=1, max_length=20)

    @field_validator("symbol", "exchange")
    @classmethod
    def uppercase_text(cls, value: str) -> str:
        return value.strip().upper()


class HoldingCreate(HoldingBase):
    portfolio_id: int = Field(gt=0)


class HoldingUpdate(BaseModel):
    quantity: Decimal | None = Field(default=None, gt=0)
    average_price: Decimal | None = Field(default=None, ge=0)
    exchange: str | None = Field(default=None, min_length=1, max_length=20)

    @field_validator("exchange")
    @classmethod
    def uppercase_exchange(cls, value: str | None) -> str | None:
        return value.strip().upper() if value is not None else None


class HoldingRead(HoldingBase):
    id: int
    portfolio_id: int

    model_config = ConfigDict(from_attributes=True)
