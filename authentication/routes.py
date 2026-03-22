from fastapi import APIRouter, Depends

from authentication.schemas import (
    UserRegisterRequest,
    DealerRegisterRequest,
    UserLoginRequest,
    UserUpdateRequest,
    DealerUpdateRequest,
    ChangePasswordRequest,
    ResetPasswordRequest,
    GoogleTokenVerifyRequest,
)
from authentication.crud import (
    register_user,
    login_user,
    get_current_user,
    update_user,
    delete_user,
    change_password,
    reset_password,
    get_dealer_profile,
    update_dealer_profile,
    verify_google_token,
)
from utils.utils import get_token, CommonResponse
from utils.schemas import tokenResponse, commonResponse
from utils.validation import (
    loginDataValidation,
    changePasswordDataValidation,
    resetPasswordDataValidation,
)

auth_router = APIRouter(prefix="/auth")


# ======================== Public Routes ========================


@auth_router.post("/register", response_model=tokenResponse)
def register(data: DealerRegisterRequest):
    """Register a new customer user."""
    return register_user(data)


@auth_router.post("/login", response_model=tokenResponse)
def login(data: UserLoginRequest):
    """Authenticate user and return JWT tokens."""
    validation_error = loginDataValidation(data)
    if validation_error:
        return CommonResponse(200, "True", 1, "Validation Error", Message=validation_error)
    return login_user(data)


@auth_router.post("/reset-password", response_model=commonResponse)
def reset_password_route(data: ResetPasswordRequest):
    """Reset password (typically after OTP verification)."""
    validation_error = resetPasswordDataValidation(data)
    if validation_error:
        return CommonResponse(200, "True", 1, "Validation Error", Message=validation_error)
    return reset_password(data)


@auth_router.post("/verify/google_access_token", summary="Verify Google token", response_model=tokenResponse)
def google_login(data: GoogleTokenVerifyRequest):
    """Verify a Google access token and login or register the user."""
    return verify_google_token(data)


# ======================== Protected Routes ========================


@auth_router.get("/user", response_model=commonResponse)
def get_me(token: dict = Depends(get_token)):
    """Get the current authenticated user's profile."""
    return get_current_user(token["email"])


@auth_router.put("/user", response_model=commonResponse)
def update_me(data: UserUpdateRequest, token: dict = Depends(get_token)):
    """Update the current authenticated user's profile."""
    return update_user(token["email"], data)


@auth_router.delete("/user", response_model=commonResponse)
def delete_me(token: dict = Depends(get_token)):
    """Deactivate the current authenticated user's account."""
    return delete_user(token["email"])


@auth_router.post("/change-password", response_model=commonResponse)
def change_password_route(data: ChangePasswordRequest, token: dict = Depends(get_token)):
    """Change password for the authenticated user."""
    validation_error = changePasswordDataValidation(data)
    if validation_error:
        return CommonResponse(200, "True", 1, "Validation Error", Message=validation_error)
    return change_password(token["email"], data)


# ======================== Dealer Routes ========================


@auth_router.get("/dealer/profile", response_model=commonResponse)
def get_dealer(token: dict = Depends(get_token)):
    """Get the dealer profile for the authenticated dealer."""
    return get_dealer_profile(token["email"])


@auth_router.put("/dealer/profile", response_model=commonResponse)
def update_dealer(data: DealerUpdateRequest, token: dict = Depends(get_token)):
    """Update the dealer profile for the authenticated dealer."""
    return update_dealer_profile(token["email"], data)
