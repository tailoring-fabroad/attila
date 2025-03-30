from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

from app.core.config import get_app_settings
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.toolkit.response import response_error, response_validation_error
from app.controllers.routes.factory import router as factory_router

def get_application() -> FastAPI:
    settings = get_app_settings()

    settings.configure_logging()

    application = FastAPI(**settings.fastapi_kwargs)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_event_handler(
        "startup",
        create_start_app_handler(application, settings),
    )
    application.add_event_handler(
        "shutdown",
        create_stop_app_handler(application),
    )

    application.add_exception_handler(HTTPException, response_error)
    application.add_exception_handler(RequestValidationError, response_validation_error)

    application.include_router(factory_router, prefix=settings.api_prefix)

    return application

app = get_application()
