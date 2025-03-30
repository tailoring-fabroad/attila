from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from typing import Any, List, Optional, Union
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from starlette.requests import Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

async def response_success(
        data: Optional[Any] = None, 
        message: str = "Success", 
        status_code: int = 200,
        ) -> JSONResponse:
    return JSONResponse(
        content={
            "code":status_code,
            "message": message,
            "data": data,
        },
        status_code=status_code,
    )

def error_response(
    status_code: int,
    message: Union[str, List[str]],
    errors: Optional[List[Any]] = None,
) -> JSONResponse:
    return JSONResponse(
        content={
            "code": status_code,
            "message": message,
            "errors": errors or [],
        },
        status_code=status_code,
    )

async def response_error(
    _: Request,
    e: HTTPException,
) -> JSONResponse:
    return error_response(
        status_code=e.status_code,
        message=e.detail if isinstance(e.detail, str) else "Error occurred",
        errors=[e.detail] if isinstance(e.detail, str) else e.detail,
    )

async def response_validation_error(
    _: Request,
    exc: Union[RequestValidationError, ValidationError],
) -> JSONResponse:
    return error_response(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation Failed",
        errors=exc.errors(),
    )
