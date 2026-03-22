from datetime import datetime, timedelta
from typing import Dict, Union, Any
from fastapi import Depends, HTTPException, status
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from pydantic import BaseModel
import config
import typing as t
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
import random

def create_access_token(subject: Union[str, Any], expires_delta: int = config.settings.ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    try:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(
            to_encode, config.settings.JWT_SECRET_KEY, config.settings.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        return str(e)


def create_refresh_token(subject: Union[str, Any], expires_delta: int = config.settings.REFRESH_TOKEN_EXPIRE_MINUTES) -> str:
    try:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(
            to_encode, config.settings.JWT_REFRESH_SECRET_KEY, config.settings.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        return str(e)


def verify_access_token(jwt_token: str) -> Dict[str, Union[bool, str]]:
    try:
        decoded_jwt = jwt.decode(
            jwt_token, config.settings.JWT_SECRET_KEY, config.settings.ALGORITHM)
        # print(decoded_jwt)
        return {'verified': True, 'email': decoded_jwt['sub']}
    except (ExpiredSignatureError, Exception, InvalidSignatureError) as e:
        print(e)
        return {'verified': False, 'email': ''}


def CommonResponse(Response: int, Error: str, ErrorCode: int, ResponseMessage: str, Message: Any, Value: Any = None):
    return {
        "status": [{
            "Response": Response,
            "Error": Error,
            "ErrorCode": ErrorCode,
            "ResponseMessage": ResponseMessage,
            "Message": Message
        }],
        "value": Value
    }


def TokenResponse(access_token: str, refresh_token: str, Response: int, Error: str, ErrorCode: int, ResponseMessage: str, Message: str, Value: Any = None):
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "status": [{
            "Response": Response,
            "Error": Error,
            "ErrorCode": ErrorCode,
            "ResponseMessage": ResponseMessage,
            "Message": Message

        }],
        "value": Value
    }
    


def UserResponse(user: Dict, Response: int, Error: str, ErrorCode: int, ResponseMessage: str, Message: Any):
    return {
        "user": user,
        "status": [{
            "Response": Response,
            "Error": Error,
            "ErrorCode": ErrorCode,
            "ResponseMessage": ResponseMessage,
            "Message": Message
        }]
    }


def otpResponse(token: str, Response: int, Error: str, ErrorCode: int, ResponseMessage: str, Message: str, Value: Any = None):
    return {
        "token": token,
        "status": [{
            "Response": Response,
            "Error": Error,
            "ErrorCode": ErrorCode,
            "ResponseMessage": ResponseMessage,
            "Message": Message

        }],
        "value": Value
    }
    
def paymentResponse(order: dict, Response: int, Error: str, ErrorCode: int, ResponseMessage: str, Message: str):
    return {
        "order": order,
        "status": [{
            "Response": Response,
            "Error": Error,
            "ErrorCode": ErrorCode,
            "ResponseMessage": ResponseMessage,
            "Message": Message
        }]
    }



# ****************************************************** Authorization Module ******************************************************


class UnauthorizedMessage(BaseModel):
    detail: str = "Unauthenticated User, Please login first."


get_bearer_token = HTTPBearer(auto_error=False)


async def get_token(
        auth: t.Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),) -> Dict[str, str]:

    # print(auth)
    if auth is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UnauthorizedMessage().detail,
        )

    verification = verify_access_token(auth.credentials)
    # print(verification)
    if not verification['verified']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UnauthorizedMessage().detail,
        )

    return {'token': auth.credentials, 'email': str(verification['email'])}

# ******************************************************  Generate OTP ******************************************************

def generate_otp():
    otp = random.randint(100000, 999999)  # Generate a random 6-digit OTP
    return otp