import uuid
import re
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TransactionRequest(BaseModel):
    user_id: uuid.UUID
    amount: Decimal = Field(..., gt=0, le=999999.99, decimal_places=2)
    currency: str = Field(default='USD', min_length=3, max_length=3)
    merchant_name: str = Field(..., min_length=1, max_length=255)
    merchant_category: Optional[str] = Field(None, max_length=100)
    location_lat: Optional[float] = Field(None, ge=-90, le=90)
    location_lng: Optional[float] = Field(None, ge=-180, le=180)
    card_last_four: Optional[str] = Field(None, min_length=4, max_length=4)

    @field_validator('merchant_name', 'merchant_category', mode='before')
    @classmethod
    def strip_html(cls, v):
        if v:
            return re.sub(r'<[^>]+>', '', str(v)).strip()
        return v


class TransactionResponse(BaseModel):
    transaction_id: uuid.UUID
    status: str
    risk_score: Optional[float]
    reason: Optional[str]
    rule_triggered: Optional[str]
    processing_time_ms: int
