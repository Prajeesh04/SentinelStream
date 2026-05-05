from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Literal
import uuid


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: Literal['user', 'admin']
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
