import asyncio
import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ------------------------------------------------------------------ #
# Alembic config                                                       #
# ------------------------------------------------------------------ #
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ------------------------------------------------------------------ #
# Import Base + ALL models so Alembic sees every table                #
# ------------------------------------------------------------------ #
from app.core.database import Base  # noqa: E402
from app.modules.bookings.infrastructure.models import (  # noqa: F401, E402
    BookedSeatModel, BookingModel)
from app.modules.trips.infrastructure.models import (  # noqa: F401, E402
    RouteModel, TripModel)
from app.modules.users.infrastructure.models import (  # noqa: F401, E402
    DriverModel, OperatorProfileModel, UserModel)

target_metadata = Base.metadata

# ------------------------------------------------------------------ #
# Read DATABASE_URL from env                                           #
# ------------------------------------------------------------------ #
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

config.set_main_option("sqlalchemy.url", DATABASE_URL)


# ------------------------------------------------------------------ #
# Migration runners                                                    #
# ------------------------------------------------------------------ #
def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
        connect_args={"server_settings": {"search_path": "public"}},
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()