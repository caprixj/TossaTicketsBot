from abc import ABC
from sqlite3 import IntegrityError
from typing import Optional, List

import aiosqlite

from model.database.artifact import Artifact
from model.database.award import Award
from model.database.member import Member
from model.database.transactions.addt_transaction import AddtTransaction
from model.database.transactions.delt_transaction import DeltTransaction
from model.database.transactions.tpay_transaction import TpayTransaction
from repository.ordering_type import OrderingType
from utilities.sql_scripts import SELECT_TOPT, SELECT_TOPTALL, INSERT_MEMBER, INSERT_DELT, INSERT_ADDT, \
    UPDATE_TICKETS_COUNT, UPDATE_MEMBER, SELECT_MEMBER_BY_USER_ID, SELECT_MEMBER_BY_USERNAME, \
    INSERT_TPAY, UPDATE_TPAY_AVAILABLE, INSERT_AWARD, SELECT_AWARD, INSERT_AWARD_MEMBER, \
    SELECT_AWARDS_BY_OWNER_ID, SELECT_AWARDS_COUNT_BY_OWNER_ID, SELECT_ARTIFACTS_COUNT_BY_OWNER_ID, \
    SELECT_ARTIFACTS_BY_OWNER_ID, SELECT_AWARD_ADDT_TIME_BY_USER_ID


class Repository(ABC):
    def __init__(self, db_path: str = None):
        self.db_path = db_path

    """ Execute """

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

    """ Create """

    async def create_member(self, member: Member) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(INSERT_MEMBER, (
                member.user_id,
                member.username,
                member.first_name,
                member.last_name,
                member.tickets
            ))
            await db.commit()

    async def create_stat_addt(self, addt: AddtTransaction) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(INSERT_ADDT, (
                addt.user_id,
                addt.tickets,
                addt.time,
                addt.description,
                addt.type_
            ))
            await db.commit()

    async def create_stat_delt(self, delt: DeltTransaction) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(INSERT_DELT, (
                delt.user_id,
                delt.tickets,
                delt.time,
                delt.description,
                delt.type_
            ))
            await db.commit()

    async def create_stat_tpay(self, tpay: TpayTransaction):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(INSERT_TPAY, (
                tpay.sender_id,
                tpay.receiver_id,
                tpay.transfer,
                tpay.fee,
                tpay.time,
                tpay.description
            ))
            await db.commit()

    async def create_award(self, award: Award):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(INSERT_AWARD, (
                award.award_id,
                award.name,
                award.description,
                award.payment
            ))
            await db.commit()

    async def create_award_member(self, award: Award, member: Member) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(INSERT_AWARD_MEMBER, (
                    award.award_id,
                    member.user_id
                ))
                await db.commit()
                return True
            except IntegrityError:
                return False

    """ Read """

    async def get_member_by_user_id(self, user_id: int) -> Optional[Member]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(SELECT_MEMBER_BY_USER_ID, (user_id,))
            row = await cursor.fetchone()
            return Member(*row) if row else None

    async def get_member_by_username(self, username: str) -> Optional[Member]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(SELECT_MEMBER_BY_USERNAME, (username,))
            row = await cursor.fetchone()
            return Member(*row) if row else None

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

    async def get_artifacts(self, user_id: int) -> List[Artifact]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(SELECT_ARTIFACTS_BY_OWNER_ID, (user_id,))
            rows = await cursor.fetchall()  # rows: list[tuple[str]]
            return [Artifact(*row) for row in rows]

    async def get_artifacts_count(self, user_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(SELECT_ARTIFACTS_COUNT_BY_OWNER_ID, (user_id, ))
            rows = await cursor.fetchall()
            return int(rows[0][0]) if rows else 0

    async def get_award(self, award_id: str) -> Optional[Award]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(SELECT_AWARD, (award_id,))
            row = await cursor.fetchone()
            return Award(*row) if row else None

    async def get_awards(self, user_id: int) -> List[Award]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(SELECT_AWARDS_BY_OWNER_ID, (user_id,))
            rows = await cursor.fetchall()
            return [Award(*row) for row in rows]

    async def get_awards_count(self, user_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(SELECT_AWARDS_COUNT_BY_OWNER_ID, (user_id,))
            rows = await cursor.fetchall()
            return int(rows[0][0]) if rows else 0

    async def get_award_addt_time(self, user_id: int) -> str:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(SELECT_AWARD_ADDT_TIME_BY_USER_ID, (user_id,))
            rows = await cursor.fetchall()
            return rows[0][0] if rows else 'not found'

    """ Update """

    async def update_member_names(self, member: Member) -> None:
        await self._execute(UPDATE_MEMBER, (
            member.username,
            member.first_name,
            member.last_name,
            member.user_id
        ))

    async def update_member_tickets(self, member: Member) -> None:
        await self._execute(UPDATE_TICKETS_COUNT, (
            member.tickets,
            member.user_id
        ))

    async def spend_tpay_available(self, member: Member):
        await self._execute(UPDATE_TPAY_AVAILABLE, (
            member.tpay_available - 1,
            member.user_id
        ))
