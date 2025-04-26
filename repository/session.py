from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from model.database import Base
from resources.const import glob

_async_engine: any = None
_AsyncSessionLocal: any = None


async def set_database():
    async with _get_async_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_async_session():
    global _async_engine, _AsyncSessionLocal

    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(_get_async_engine(), expire_on_commit=False)

    return _AsyncSessionLocal


def _get_async_engine():
    global _async_engine

    _async_engine = create_async_engine(f"sqlite+aiosqlite:///{glob.rms.db_file_path}", echo=True) \
        if _async_engine is None else _async_engine

    return _async_engine
