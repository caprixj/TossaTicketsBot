import aiosqlite
import json
from abc import ABC
from typing import Optional

from model.Member import Member


class MemberRepository(ABC):
    def __init__(self, db_path: str = None):
        self.db_path = db_path

    async def _execute(self, query: str, params: tuple = ()):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return cursor

    async def create(self, member: Member) -> None:
        query = ("INSERT INTO members (user_id, username, first_name, last_name, tickets_count, unique_artifacts)"
                 " VALUES (?, ?, ?, ?, ?, ?)")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, (
                member.user_id,
                member.username,
                member.first_name,
                member.last_name,
                member.tickets_count,
                member.unique_artifacts
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
        query = "UPDATE members SET username = ?, first_name = ?, last_name = ?, WHERE user_id = ?"
        await self._execute(query, (
            member.username,
            member.first_name,
            member.last_name,
            member.user_id
        ))

    async def update_tickets_count(self, member: Member) -> None:
        query = "UPDATE members SET tickets_count = ? WHERE user_id = ?"
        print(f'{member.tickets_count}, {member.user_id}')
        await self._execute(query, (
            member.tickets_count,
            member.user_id
        ))

    async def update_unique_artifacts(self, member: Member) -> None:
        query = "UPDATE members SET unique_artifacts = ? WHERE user_id = ?"
        await self._execute(query, (
            json.dumps(member.unique_artifacts),
            member.user_id
        ))

    async def list(self) -> list[Member]:
        query = "SELECT * FROM members"
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query)
            rows = await cursor.fetchall()
            return [Member(*row) for row in rows]
