import logging
import sys
from typing import Any, Dict, List, Tuple, Optional

from loguru import logger
from pydantic import PostgresDsn, SecretStr, root_validator

from app.core.logging import InterceptHandler
from app.core.settings.base import BaseAppSettings

class AppSettings(BaseAppSettings):
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "FastAPI application"
    version: str = "0.0.0"

    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    database_url: Optional[PostgresDsn] = None
    max_connection_count: int = 10
    min_connection_count: int = 10

    secret_key: SecretStr

    gcp_credential: Optional[str]
    gcp_projectid: Optional[str]
    gcp_bucketname: Optional[str]
    gcp_path: Optional[str]

    api_prefix: str = "/api"

    jwt_token_prefix: str = "Bearer"

    allowed_hosts: List[str] = ["*"]

    logging_level: int = logging.INFO
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    @root_validator(pre=True)
    def assemble_db_url(cls, values):
        if not values.get("database_url"):
            values["database_url"] = (
                f"postgresql://{values['db_user']}:{values['db_password']}@"
                f"{values['db_host']}:{values['db_port']}/{values['db_name']}"
            )
        return values

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }

    def configure_logging(self) -> None:
        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in self.loggers:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [InterceptHandler(level=self.logging_level)]

        logger.configure(handlers=[{"sink": sys.stderr, "level": self.logging_level}])
