from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True
