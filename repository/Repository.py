import aiosqlite
import json
from abc import ABC
from typing import Optional

from model.database.Member import Member
from model.database.transactions.AddtTransaction import AddtTransaction
from model.database.transactions.DeltTransaction import DeltTransaction
from repository.OrderingType import OrderingType
from utilities.sqlscripts import SELECT_TOPT, SELECT_TOPTALL


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
        query = ("INSERT INTO members (user_id, username, first_name, last_name, tickets_count, artifacts)"
                 " VALUES (?, ?, ?, ?, ?, ?)")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, (
                member.user_id,
                member.username,
                member.first_name,
                member.last_name,
                member.tickets_count
            ))
            await db.commit()

    async def read(self, user_id: int) -> Optional[Member]:
        query = "SELECT * FROM members WHERE user_id = ?"
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, (user_id,))
            row = await cursor.fetchone()
            return Member(*row) if row else None

    async def delete(self, user_id: int) -> None:
        query = "DELETE FROM members WHERE user_id = ?"
        await self._execute(query, (user_id,))

    async def update_names(self, member: Member) -> None:
        query = "UPDATE members SET username = ?, first_name = ?, last_name = ? WHERE user_id = ?"
        await self._execute(query, (
            member.username,
            member.first_name,
            member.last_name,
            member.user_id
        ))

    async def update_tickets_count(self, member: Member) -> None:
        query = "UPDATE members SET tickets_count = ? WHERE user_id = ?"
        await self._execute(query, (
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
        query = "SELECT tickets_count FROM members WHERE user_id = ?"
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, (user_id,))
            return int((await cursor.fetchone())[0])

    async def get_artifact_names_by_user_id(self, user_id: int) -> list[str]:
        query = "SELECT a.name FROM artifacts a WHERE owner_id = ?"
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, (user_id,))
            rows = await cursor.fetchall()  # rows: list[tuple[str]]
            return [row[0] for row in rows]

    async def add_stat_addt(self, addt: AddtTransaction) -> None:
        query = ("INSERT INTO addt (user_id, tickets_count, transaction_time, description)"
                 " VALUES (?, ?, ?, ?)")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, (
                addt.user_id,
                addt.tickets_count,
                addt.transaction_time,
                addt.description
            ))
            await db.commit()

    async def add_stat_delt(self, delt: DeltTransaction) -> None:
        query = ("INSERT INTO delt (user_id, tickets_count, transaction_time, description)"
                 " VALUES (?, ?, ?, ?)")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, (
                delt.user_id,
                delt.tickets_count,
                delt.transaction_time,
                delt.description
            ))
            await db.commit()
