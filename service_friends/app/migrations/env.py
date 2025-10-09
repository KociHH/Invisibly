import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config, text
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL")
schema = os.getenv("SERVICE_FRIENDS_NAME_SCHEMA")

from app.db.sql.tables import FriendUser, SendFriendRequest, base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def include_name(name, type_, parent_names):
    if type_ == "schema":
        return name == schema
    if type_ == "table":
        return parent_names.get("schema_name") == schema
    return True

def run_migrations_offline() -> None:
    context.configure(
        url=POSTGRES_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        include_name=include_name,
        dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        include_name=include_name,
        version_table_schema=schema
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    
    connectable = create_async_engine(POSTGRES_URL)
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def run_migrations_online() -> None:
    
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

