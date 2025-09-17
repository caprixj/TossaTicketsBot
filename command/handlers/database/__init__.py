from .sqlsf import router as sql
from .db import router as db

database_routers = [sql, db]
