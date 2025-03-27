from sqlite3 import IntegrityError
from typing import Optional, List

import aiosqlite
from aiosqlite import Cursor

from model.database.artifact import Artifact
from model.database.award import Award
from model.database.member import Member
from model.database.addt_transaction import AddtTransaction
from model.database.delt_transaction import DeltTransaction
from model.database.tpay_transaction import TpayTransaction
from model.results.mytpay_result import MytpayResult
from model.types.transaction_type import TransactionType
from repository.ordering_type import OrderingType
from resources.const import glob
from sql import scripts


async def _get_unique_members(cursor: Cursor, user_id: int, tpays: List[TpayTransaction]) -> List[Member]:
    unique_ids = set()
    unique_members = list()

    for tt in tpays:
        if tt.sender_id != user_id:
            unique_ids.add(tt.sender_id)
        if tt.receiver_id != user_id:
            unique_ids.add(tt.receiver_id)

    for member_id in unique_ids:
        await cursor.execute(scripts.SELECT_MEMBER_BY_USER_ID, (member_id,))
        row = await cursor.fetchone()
        unique_members.append(Member(*row) if row else None)

    return unique_members


async def _execute(query: str, params: tuple = ()):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor


""" Execute """


async def execute_external(query: str) -> (bool, str):
    try:
        result = str()
        async with aiosqlite.connect(glob.rms.db_file_path) as db:
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


async def create_member(member: Member) -> None:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_MEMBER, (
            member.user_id,
            member.username,
            member.first_name,
            member.last_name,
            member.tickets
        ))
        await db.commit()


async def create_stat_addt(addt: AddtTransaction) -> None:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_ADDT, (
            addt.user_id,
            addt.tickets,
            addt.time,
            addt.description,
            addt.type_
        ))
        await db.commit()


async def create_stat_delt(delt: DeltTransaction) -> None:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_DELT, (
            delt.user_id,
            delt.tickets,
            delt.time,
            delt.description,
            delt.type_
        ))
        await db.commit()


async def create_stat_tpay(tpay: TpayTransaction):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_TPAY, (
            tpay.sender_id,
            tpay.receiver_id,
            tpay.transfer,
            tpay.fee,
            tpay.time,
            tpay.description
        ))
        await db.commit()


async def create_award(award: Award):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_AWARD, (
            award.award_id,
            award.name,
            award.description,
            award.payment
        ))
        await db.commit()


async def create_award_member(award: Award, member: Member) -> bool:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        try:
            await db.execute(scripts.INSERT_AWARD_MEMBER, (
                award.award_id,
                member.user_id
            ))
            await db.commit()
            return True
        except IntegrityError:
            return False


""" Read """


async def get_member_by_user_id(user_id: int) -> Optional[Member]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_MEMBER_BY_USER_ID, (user_id,))
        row = await cursor.fetchone()
        return Member(*row) if row else None


async def get_member_by_username(username: str) -> Optional[Member]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_MEMBER_BY_USERNAME, (username,))
        row = await cursor.fetchone()
        return Member(*row) if row else None


async def get_members_by_tickets() -> list[Member]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_TOPTALL)
        rows = await cursor.fetchall()
        return [Member(*row) for row in rows]


async def get_members_by_tickets_limited(order: OrderingType, size: int) -> list[Member]:
    query = scripts.SELECT_TOPT.replace('$', order.value)

    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(query, (abs(size),))
        rows = await cursor.fetchall()
        return [Member(*row) for row in rows]


async def get_artifacts(user_id: int) -> List[Artifact]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_ARTIFACTS_BY_OWNER_ID, (user_id,))
        rows = await cursor.fetchall()  # rows: list[tuple[str]]
        return [Artifact(*row) for row in rows]


async def get_artifacts_count(user_id: int) -> int:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_ARTIFACTS_COUNT_BY_OWNER_ID, (user_id,))
        row = await cursor.fetchone()
        return int(row[0]) if row else 0


async def get_award(award_id: str) -> Optional[Award]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_AWARD, (award_id,))
        row = await cursor.fetchone()
        return Award(*row) if row else None


async def get_awards(user_id: int) -> List[Award]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_AWARDS_BY_OWNER_ID, (user_id,))
        rows = await cursor.fetchall()
        return [Award(*row) for row in rows]


async def get_awards_count(user_id: int) -> int:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_AWARDS_COUNT_BY_OWNER_ID, (user_id,))
        row = await cursor.fetchone()
        return int(row[0]) if row else 0


async def get_award_addt_time(user_id: int) -> str:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_AWARD_ADDT_TIME_BY_USER_ID, (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else 'not found'


async def get_transaction_stats(user_id: int) -> MytpayResult:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.cursor()

        # tpays
        await cursor.execute(scripts.SELECT_TPAY_BY_SENDER_OR_RECEIVER, (user_id, user_id))
        tpays = await cursor.fetchall()
        tpays = [TpayTransaction(*row) for row in tpays]

        # addts
        await cursor.execute(
            scripts.SELECT_ADDT_TYPE_NOT_TPAY,
            (user_id, TransactionType.tpay, TransactionType.tpay_fee)
        )
        addts = await cursor.fetchall()
        addts = [AddtTransaction(*row) for row in addts]

        # delts
        await cursor.execute(
            scripts.SELECT_DELT_TYPE_NOT_TPAY,
            (user_id, TransactionType.tpay, TransactionType.tpay_fee)
        )
        delts = await cursor.fetchall()
        delts = [DeltTransaction(*row) for row in delts]

        # unique_tpay_members
        unique_tpay_members = await _get_unique_members(cursor, user_id, tpays)

        return MytpayResult(user_id, tpays, addts, delts, unique_tpay_members)


""" Update """


async def update_member_names(member: Member) -> None:
    await _execute(scripts.UPDATE_MEMBER, (
        member.username,
        member.first_name,
        member.last_name,
        member.user_id
    ))


async def update_member_tickets(member: Member) -> None:
    await _execute(scripts.UPDATE_TICKETS_COUNT, (
        member.tickets,
        member.user_id
    ))


async def spend_tpay_available(member: Member):
    await _execute(scripts.UPDATE_TPAY_AVAILABLE, (
        member.tpay_available - 1,
        member.user_id
    ))
