import os
from logging.config import fileConfig

# --- CHANGED: This path fix now works in all environments ---
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
# --- End Path Fix ---

from sqlalchemy import engine_from_config
from sqlalchemy.engine import URL
from sqlalchemy import pool

from alembic import context

# --- CHANGED: Import from 'src.' ---
from models import Base
from database import settings


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- CUSTOM CONFIG ---
target_metadata = Base.metadata

# Set the sqlalchemy.url from our .env settings
db_url = URL.create(
    drivername="postgresql",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    database=settings.POSTGRES_DB,
)
config.set_main_option('sqlalchemy.url', db_url.render_as_string(hide_password=False))
# --- END CUSTOM CONFIG ---


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_online()
else:
    run_migrations_online()