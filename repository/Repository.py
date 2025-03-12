import aiosqlite
from abc import ABC
from typing import Optional

from model.database.Member import Member
from model.database.transactions.AddtTransaction import AddtTransaction
from model.database.transactions.DeltTransaction import DeltTransaction
from repository.OrderingType import OrderingType
from utilities.sql_scripts import SELECT_TOPT, SELECT_TOPTALL, INSERT_MEMBER, INSERT_DELT, INSERT_ADDT, \
    SELECT_ARTIFACT_NAMES, SELECT_TICKETS_COUNT, UPDATE_TICKETS_COUNT, UPDATE_MEMBER, DELETE_MEMBER, \
    SELECT_MEMBER_BY_USER_ID, SELECT_MEMBER_BY_USERNAME


class Repository(ABC):
    def __init__(self, db_path: str = None):
        self.db_path = db_path

    async def _execute(self, query: str, params: tuple = ()):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return cursor

    async def execute_external(self, query: str) -> (bool, str):
        try:
            result = str()
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(query)
                if query.strip().lower().startswith('select'):
                    rows = await cursor.fetchall()
                    for r in rows:
                        for f in r:
                            result += f'{f} | '
                        result = f'{result[:-3]}\n'
                else:
                    await db.commit()
                    result = str(cursor.rowcount)
            return True, result
        except Exception as e:
            return False, str(e)

    async def create(self, member: Member) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(INSERT_MEMBER, (
                member.user_id,
                member.username,
                member.first_name,
                member.last_name,
                member.tickets_count
            ))
            await db.commit()

    async def read_by_user_id(self, user_id: int) -> Optional[Member]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(SELECT_MEMBER_BY_USER_ID, (user_id,))
            row = await cursor.fetchone()
            return Member(*row) if row else None

    async def read_by_username(self, username: str) -> Optional[Member]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(SELECT_MEMBER_BY_USERNAME, (username,))
            row = await cursor.fetchone()
            return Member(*row) if row else None

    async def delete(self, user_id: int) -> None:
        await self._execute(DELETE_MEMBER, (user_id,))

    async def update_names(self, member: Member) -> None:
        await self._execute(UPDATE_MEMBER, (
            member.username,
            member.first_name,
            member.last_name,
            member.user_id
        ))

    async def update_tickets_count(self, member: Member) -> None:
        await self._execute(UPDATE_TICKETS_COUNT, (
            member.tickets_count,
            member.user_id
        ))

    async def get_members_by_tickets(self) -> list[Member]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(SELECT_TOPTALL)
            rows = await cursor.fetchall()
            return [Member(*row) for row in rows]

    async def get_members_by_tickets_limited(self, order: OrderingType, size: int) -> list[Member]:
        query = SELECT_TOPT.replace('$', order.value)
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, (abs(size),))
            rows = await cursor.fetchall()
            return [Member(*row) for row in rows]

    async def get_member_tickets_count(self, user_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(SELECT_TICKETS_COUNT, (user_id,))
            return int((await cursor.fetchone())[0])

    async def get_artifact_names_by_user_id(self, user_id: int) -> list[str]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(SELECT_ARTIFACT_NAMES, (user_id,))
            rows = await cursor.fetchall()  # rows: list[tuple[str]]
            return [row[0] for row in rows]

    async def add_stat_addt(self, addt: AddtTransaction) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(INSERT_ADDT, (
                addt.user_id,
                addt.tickets_count,
                addt.transaction_time,
                addt.description
            ))
            await db.commit()

    async def add_stat_delt(self, delt: DeltTransaction) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(INSERT_DELT, (
                delt.user_id,
                delt.tickets_count,
                delt.transaction_time,
                delt.description
            ))
            await db.commit()
