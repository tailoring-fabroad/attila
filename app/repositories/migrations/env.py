import os
import pathlib
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

BASE_DIR = pathlib.Path(__file__).resolve().parents[3]  
sys.path.append(str(BASE_DIR))

from app.core.config import get_app_settings
# from app.models.base import Base  

SETTINGS = get_app_settings()
DATABASE_URL = SETTINGS.database_url

print("ENV values before validation:", DATABASE_URL)

config = context.config
fileConfig(config.config_file_name)

target_metadata = None
# target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", str(DATABASE_URL))


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
