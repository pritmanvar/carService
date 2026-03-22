from uuid import uuid4

import requests
from django.contrib.auth.hashers import check_password

from authentication.models import User, Customer, Dealer
from authentication.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserUpdateRequest,
    DealerUpdateRequest,
    ChangePasswordRequest,
    ResetPasswordRequest,
    GoogleTokenVerifyRequest,
)
from utils.utils import (
    create_access_token,
    create_refresh_token,
    CommonResponse,
    TokenResponse,
)


# ======================== Helpers ========================


def _user_to_dict(user: User) -> dict:
    """Serialize a User instance to a plain dict."""
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "phone_number": user.phone_number,
        "address": user.address,
        "user_type": user.user_type,
        "is_google_login": user.is_google_login,
    }


def _dealer_to_dict(dealer: Dealer) -> dict:
    return {
        "company_name": dealer.company_name,
        "crm_webhook_url": dealer.crm_webhook_url,
        "user": _user_to_dict(dealer.user),
    }


# ======================== Register ========================


def register_user(data: UserRegisterRequest):
    """Create a new User and the associated Customer or Dealer profile."""
    try:
        if User.objects.filter(email=data.email).exists():
            return TokenResponse("", "", 200, "True", 1, "Failed", Message="Email is already in use.")

        user_type = data.role  # 'customer' or 'dealer'

        user = User.objects.create_user(
            username=data.email,
            email=data.email,
            password=data.password,
            name=data.name,
            phone_number=data.phone_number,
            address=data.address,
            user_type=user_type,
        )

        if user_type == "dealer":
            company_name = getattr(data, "company_name", None)
            crm_webhook_url = getattr(data, "crm_webhook_url", None)
            Dealer.objects.create(
                user=user,
                company_name=company_name,
                crm_webhook_url=crm_webhook_url,
            )
        else:
            Customer.objects.create(user=user)

        access_token = create_access_token(user.email)
        refresh_token = create_refresh_token(user.email)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            Response=201,
            Error="False",
            ErrorCode=0,
            ResponseMessage="Success",
            Message="Registration successful.",
            Value=_user_to_dict(user),
        )

    except Exception as e:
        return TokenResponse("", "", 200, "True", 0, "Failed", Message=str(e))


# ======================== Login ========================


def login_user(data: UserLoginRequest):
    """Authenticate a user with email & password and return JWT tokens."""
    try:
        try:
            user = User.objects.get(email=data.email)
        except User.DoesNotExist:
            return TokenResponse("", "", 200, "True", 1, "Failed", Message="Invalid email or password.")

        if not check_password(data.password, user.password):
            return TokenResponse("", "", 200, "True", 1, "Failed", Message="Invalid email or password.")

        if not user.is_active:
            return TokenResponse("", "", 200, "True", 1, "Failed", Message="Account is deactivated.")

        access_token = create_access_token(user.email)
        refresh_token = create_refresh_token(user.email)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            Response=200,
            Error="False",
            ErrorCode=0,
            ResponseMessage="Success",
            Message="Login successful.",
            Value=_user_to_dict(user),
        )

    except Exception as e:
        return TokenResponse("", "", 200, "True", 0, "Failed", Message=str(e))


# ======================== Get Current User ========================


def get_current_user(email: str):
    """Return full profile for the authenticated user."""
    try:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return CommonResponse(200, "True", 1, "Failed", Message="User not found.")

        user_data = _user_to_dict(user)

        # Attach role-specific profile
        if user.user_type == "dealer":
            try:
                dealer = Dealer.objects.get(user=user)
                user_data["dealer_profile"] = {
                    "company_name": dealer.company_name,
                    "crm_webhook_url": dealer.crm_webhook_url,
                }
            except Dealer.DoesNotExist:
                pass
        else:
            try:
                Customer.objects.get(user=user)
                user_data["customer_profile"] = True
            except Customer.DoesNotExist:
                pass

        return CommonResponse(
            Response=200,
            Error="False",
            ErrorCode=0,
            ResponseMessage="Success",
            Message="User fetched successfully.",
            Value=user_data,
        )

    except Exception as e:
        return CommonResponse(200, "True", 0, "Failed", Message=str(e))


# ======================== Update User ========================


def update_user(email: str, data: UserUpdateRequest):
    """Update user profile fields."""
    try:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return CommonResponse(200, "True", 1, "Failed", Message="User not found.")

        # Check if new email is already taken by another user
        if data.email and data.email != email:
            if User.objects.filter(email=data.email).exclude(id=user.id).exists():
                return CommonResponse(200, "True", 1, "Failed", Message="Email is already in use.")

        if data.name is not None:
            user.name = data.name
        if data.email is not None:
            user.email = data.email
        if data.phone_number is not None:
            user.phone_number = data.phone_number
        if data.address is not None:
            user.address = data.address

        user.save()

        return CommonResponse(
            Response=200,
            Error="False",
            ErrorCode=0,
            ResponseMessage="Success",
            Message="User updated successfully.",
            Value=_user_to_dict(user),
        )

    except Exception as e:
        return CommonResponse(200, "True", 0, "Failed", Message=str(e))


# ======================== Delete User ========================


def delete_user(email: str):
    """Soft-delete (deactivate) the user account."""
    try:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return CommonResponse(200, "True", 1, "Failed", Message="User not found.")

        user.is_active = False
        user.save()

        return CommonResponse(200, "False", 0, "Success", Message="User account deactivated successfully.")

    except Exception as e:
        return CommonResponse(200, "True", 0, "Failed", Message=str(e))


# ======================== Change Password ========================


def change_password(email: str, data: ChangePasswordRequest):
    """Change password for the authenticated user."""
    try:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return CommonResponse(200, "True", 1, "Failed", Message="User not found.")

        if not check_password(data.old_password, user.password):
            return CommonResponse(200, "True", 1, "Failed", Message="Old password is incorrect.")

        user.set_password(data.new_password)
        user.save()

        return CommonResponse(200, "False", 0, "Success", Message="Password changed successfully.")

    except Exception as e:
        return CommonResponse(200, "True", 0, "Failed", Message=str(e))


# ======================== Reset Password ========================


def reset_password(data: ResetPasswordRequest):
    """Reset password for a user (typically after OTP verification)."""
    try:
        try:
            user = User.objects.get(email=data.email)
        except User.DoesNotExist:
            return CommonResponse(200, "True", 1, "Failed", Message="User not found.")

        user.set_password(data.new_password)
        user.save()

        return CommonResponse(200, "False", 0, "Success", Message="Password reset successfully.")

    except Exception as e:
        return CommonResponse(200, "True", 0, "Failed", Message=str(e))


# ======================== Dealer Profile ========================


def get_dealer_profile(email: str):
    """Get the dealer profile for the authenticated dealer user."""
    try:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return CommonResponse(200, "True", 1, "Failed", Message="User not found.")

        if user.user_type != "dealer":
            return CommonResponse(200, "True", 1, "Failed", Message="User is not a dealer.")

        try:
            dealer = Dealer.objects.get(user=user)
        except Dealer.DoesNotExist:
            return CommonResponse(200, "True", 1, "Failed", Message="Dealer profile not found.")

        return CommonResponse(
            Response=200,
            Error="False",
            ErrorCode=0,
            ResponseMessage="Success",
            Message="Dealer profile fetched successfully.",
            Value=_dealer_to_dict(dealer),
        )

    except Exception as e:
        return CommonResponse(200, "True", 0, "Failed", Message=str(e))


# ======================== Google Login ========================


def verify_google_token(data: GoogleTokenVerifyRequest):
    """Verify a Google access token and login or register the user."""
    try:
        url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={data.access_token}"
        response = requests.get(url)

        if response.status_code != 200:
            return TokenResponse(
                access_token="",
                refresh_token="",
                Response=401,
                Error="True",
                ErrorCode=0,
                ResponseMessage="Failed",
                Message="Invalid Google token.",
            )

        profile = response.json()
        google_email = profile.get("email")

        if not google_email:
            return TokenResponse(
                access_token="",
                refresh_token="",
                Response=401,
                Error="True",
                ErrorCode=0,
                ResponseMessage="Failed",
                Message="Could not retrieve email from Google token.",
            )

        # Get existing user or create a new one
        try:
            user = User.objects.get(email=google_email)
        except User.DoesNotExist:
            user_type = data.role or "customer"
            user = User.objects.create_user(
                username=google_email,
                email=google_email,
                password=str(uuid4()),
                is_google_login=True,
                name=data.name or profile.get("name"),
                phone_number=data.phone_number,
                address=data.address,
                user_type=user_type,
            )
            if user_type == "dealer":
                Dealer.objects.create(
                    user=user,
                    company_name=data.company_name,
                    crm_webhook_url=data.crm_webhook_url,
                )
            else:
                Customer.objects.create(user=user)

        access_token = create_access_token(user.email)
        refresh_token = create_refresh_token(user.email)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            Response=200,
            Error="False",
            ErrorCode=0,
            ResponseMessage="Success",
            Message="Successfully logged in via Google.",
            Value=_user_to_dict(user),
        )

    except Exception as e:
        return TokenResponse(
            access_token="",
            refresh_token="",
            Response=500,
            Error="True",
            ErrorCode=0,
            ResponseMessage="Something went wrong.",
            Message=str(e),
        )


def update_dealer_profile(email: str, data: DealerUpdateRequest):
    """Update dealer-specific fields (company_name, crm_webhook_url)."""
    try:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return CommonResponse(200, "True", 1, "Failed", Message="User not found.")

        if user.user_type != "dealer":
            return CommonResponse(200, "True", 1, "Failed", Message="User is not a dealer.")

        try:
            dealer = Dealer.objects.get(user=user)
        except Dealer.DoesNotExist:
            return CommonResponse(200, "True", 1, "Failed", Message="Dealer profile not found.")

        if data.company_name is not None:
            dealer.company_name = data.company_name
        if data.crm_webhook_url is not None:
            dealer.crm_webhook_url = data.crm_webhook_url

        dealer.save()

        return CommonResponse(
            Response=200,
            Error="False",
            ErrorCode=0,
            ResponseMessage="Success",
            Message="Dealer profile updated successfully.",
            Value=_dealer_to_dict(dealer),
        )

    except Exception as e:
        return CommonResponse(200, "True", 0, "Failed", Message=str(e))
