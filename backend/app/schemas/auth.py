from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    org_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}


class OrgOut(BaseModel):
    id: str
    name: str
    slug: str

    model_config = {"from_attributes": True}
