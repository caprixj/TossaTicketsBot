from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from model.database import Base
from resources.const import glob

async_engine = create_async_engine(f"sqlite+aiosqlite:///{glob.rms.db_file_path}", echo=True)
sync_engine = create_engine(f"sqlite:///{glob.rms.db_file_path}", echo=True)

Base.metadata.create_all(sync_engine, checkfirst=True)

AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)
