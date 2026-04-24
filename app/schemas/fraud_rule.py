from pydantic import BaseModel
from typing import Optional


class FraudRuleCreate(BaseModel):
    name: str
    field_name: str
    operator: str
    threshold_value: str
    action: str = 'FLAG'
    priority: int = 1
    is_active: bool = True


class FraudRuleResponse(BaseModel):
    id: int
    name: str
    field_name: str
    operator: str
    threshold_value: str
    action: str
    priority: int
    is_active: bool

    class Config:
        from_attributes = True
