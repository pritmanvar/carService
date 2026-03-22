from typing import Dict, Sequence, Any
from pydantic import BaseModel, Field


class emailVerify(BaseModel):
    email: str

    class Config:
        from_attributes = True


class sendOTP(BaseModel):
    # phoneNumber: int = 0
    email: str
    # medium: str


class verifyOTP(BaseModel):
    # phoneNumber: int
    # phoneNumberOTP: int
    email: str
    emailOTP: str


class responseParameter(BaseModel):
    Response: int
    Error: str
    ErrorCode: int
    ResponseMessage: str
    Message: Any

    class Config:
        from_attributes = True


class commonResponse(BaseModel):
    status: Sequence[responseParameter]
    value: Any
    class Config:
        from_attributes = True


class tokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    status: Sequence[responseParameter]
    value: Any

    class Config:
        from_attributes = True


class verifyOtpResponse(BaseModel):
    access_token: str
    refresh_token: str
    status: Sequence[responseParameter]

    class Config:
        from_attributes = True


class userBase(BaseModel):
    firstName: str
    lastName: str
    email: str
    phoneNumber: int

    class Config:
        from_attributes = True


class userResponse(BaseModel):
    user: Dict
    status: Sequence[responseParameter]

    class Config:
        from_attributes = True
