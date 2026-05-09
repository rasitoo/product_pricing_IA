from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from backend.src.models.base import Base
from backend.src.models import (  # noqa: F401
    ai_proposal,
    external_comparable,
    historical_reference,
    llm_metric,
    operator_review,
    product,
    product_image,
    publication_draft,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from app settings (reads .env.local) if DATABASE_URL is set there
try:
    from backend.src.config.settings import get_settings as _get_settings
    _db_url = _get_settings().database_url
    if _db_url and _db_url != "sqlite:///./app.db":
        config.set_main_option("sqlalchemy.url", _db_url)
except Exception:
    pass

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


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


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
