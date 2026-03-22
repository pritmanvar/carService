from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ======================== Request Schemas ========================


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    phone_number: Optional[int] = None
    address: Optional[str] = None
    role: str = Field(default="customer", pattern="^(customer|dealer)$")

    class Config:
        from_attributes = True


class DealerRegisterRequest(UserRegisterRequest):
    """Extended registration for dealers with company details."""
    company_name: Optional[str] = None
    crm_webhook_url: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[int] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True


class DealerUpdateRequest(BaseModel):
    company_name: Optional[str] = None
    crm_webhook_url: Optional[str] = None

    class Config:
        from_attributes = True


class GoogleTokenVerifyRequest(BaseModel):
    access_token: str
    name: Optional[str] = None
    phone_number: Optional[int] = None
    address: Optional[str] = None
    role: str = Field(default="customer", pattern="^(customer|dealer)$")
    company_name: Optional[str] = None
    crm_webhook_url: Optional[str] = None

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    class Config:
        from_attributes = True


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str

    class Config:
        from_attributes = True


# ======================== Response Schemas ========================


class UserOut(BaseModel):
    id: str
    name: Optional[str] = None
    email: str
    phone_number: Optional[int] = None
    address: Optional[str] = None
    user_type: str
    is_google_login: bool = False

    class Config:
        from_attributes = True


class CustomerOut(BaseModel):
    id: int
    user: UserOut

    class Config:
        from_attributes = True


class DealerOut(BaseModel):
    id: int
    user: UserOut
    company_name: Optional[str] = None
    crm_webhook_url: Optional[str] = None

    class Config:
        from_attributes = True
