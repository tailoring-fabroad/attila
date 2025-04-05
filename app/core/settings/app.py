import os
import logging
import sys
from typing import Any, Dict, List, Tuple, Optional

from loguru import logger
from pydantic import Field, PostgresDsn, SecretStr, root_validator

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

    db_user: Optional[str] = Field(default=None, env="DBUSER")
    db_password: Optional[str] = Field(default=None, env="DBPASSWORD")
    db_host: Optional[str] = Field(default=None, env="DBHOST")
    db_port: Optional[int] = Field(default=None, env="DBPORT")
    db_name: Optional[str] = Field(default=None, env="DBNAME")

    database_url: Optional[PostgresDsn] = None

    max_connection_count: int = 10
    min_connection_count: int = 10

    secret_key: Optional[SecretStr] = Field(default=None, env="JWT")
    secret_key_expired: Optional[int] = Field(default=1440, env="JWT_EXP")

    gcp_credential: Optional[str] = Field(default=None, env="GCP_CREDENTIAL")
    gcp_projectid: Optional[str] = Field(default=None, env="GCP_PROJECTID")
    gcp_bucketname: Optional[str] = Field(default=None, env="GCP_BUCKETNAME")
    gcp_path: Optional[str] = Field(default=None, env="GCP_PATH")

    api_prefix: str = "/api"
    jwt_token_prefix: str = "Bearer"
    allowed_hosts: List[str] = ["*"]

    logging_level: int = logging.INFO
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        validate_assignment = True

    @root_validator(pre=True)
    def assemble_credential(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        db_user = values.get("db_user") or os.environ.get("DBUSER")
        db_password = values.get("db_password") or os.environ.get("DBPASSWORD")
        db_host = values.get("db_host") or os.environ.get("DBHOST")
        db_port = values.get("db_port") or os.environ.get("DBPORT")
        db_name = values.get("db_name") or os.environ.get("DBNAME")

        if not values.get("database_url") and all([db_user, db_password, db_host, db_port, db_name]):
            values["database_url"] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        values.setdefault("db_user", db_user)
        values.setdefault("db_password", db_password)
        values.setdefault("db_host", db_host)
        values.setdefault("db_port", db_port)
        values.setdefault("db_name", db_name)

        raw_credential = values.get("gcp_credential") or os.environ.get("GCP_CREDENTIAL")
        if raw_credential:
            if os.path.exists(raw_credential):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = raw_credential
                values["gcp_credential"] = raw_credential
            else:
                print(f"[DEBUG] credential file not found at: {raw_credential}")
                raise ValueError("GCP_CREDENTIAL path does not exist or is invalid")

        return values

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
