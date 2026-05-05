from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal


class FraudRuleCreate(BaseModel):
    name: str
    field_name: str
    operator: Literal['>', '<', '==', '>=', '<=', '!=']
    threshold_value: str
    action: Literal['FLAG', 'BLOCK', 'REVIEW'] = 'FLAG'
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

    model_config = ConfigDict(from_attributes=True)
