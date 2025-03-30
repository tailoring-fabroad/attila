from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from app.core.config import get_app_settings
from app.core.settings.app import AppSettings

from app.controllers.dependencies.database import get_repository

from app.models.schemas.authentication import (RequestLogin, RequestRegister, ResponseAuthentication)
from app.repositories.data.authentication import (AuthenticationRepository, check_email_is_taken, check_username_is_taken)
from app.repositories.errors import EntityDoesNotExist

from app.toolkit.response import response_success, response_error
from app.toolkit import constants
from app.toolkit import jwt

router = APIRouter()

@router.post("/login", response_model=ResponseAuthentication, name="Login")
async def login(
    login_request:RequestLogin= Body(...),
    authentication_repository: AuthenticationRepository = Depends(get_repository(AuthenticationRepository)),
    settings: AppSettings = Depends(get_app_settings),
) -> ResponseAuthentication:

    wrong_login_error = HTTPException(
        status_code=HTTP_400_BAD_REQUEST,
        detail=constants.INCORRECT_LOGIN_INPUT,
    )

    try:
        user = await authentication_repository.get_user_by_email(email=login_request.email)
    except EntityDoesNotExist as existence_error:
        raise wrong_login_error from existence_error

    if not user.check_password(login_request.password):
        raise wrong_login_error

    access_token = jwt.create_access_token_for_user(user, str(settings.secret_key.get_secret_value()))

    return await response_success(
        status_code=HTTP_200_OK,
        message="Login Success",
        data=ResponseAuthentication(token=access_token).dict(),
    )

@router.post("/register", status_code=HTTP_201_CREATED, name="Register")
async def register(
    register_request: RequestRegister= Body(...),
    authentication_repository: AuthenticationRepository = Depends(get_repository(AuthenticationRepository)),
    settings: AppSettings = Depends(get_app_settings),
) -> ResponseAuthentication:
    
    if await check_username_is_taken(authentication_repository, register_request.username):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=constants.USERNAME_TAKEN,
        )

    if await check_email_is_taken(authentication_repository, register_request.email):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=constants.EMAIL_TAKEN,
        )

    user = await authentication_repository.create_user(**register_request.dict())

    access_token = jwt.create_access_token_for_user(user, str(settings.secret_key.get_secret_value()))

    return await response_success(
        status_code=HTTP_201_CREATED,
        message="Registered Successfully",
        data=ResponseAuthentication(token=access_token).dict(),
    )
