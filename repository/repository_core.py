from datetime import datetime, timedelta
from sqlite3 import IntegrityError
from typing import Optional, List

import aiosqlite
from aiosqlite import Cursor

from model.database.artifact import Artifact
from model.database.award import Award
from model.database.award_member import AwardMemberJunction
from model.database.member import Member
from model.database.addt_transaction import AddtTransaction
from model.database.delt_transaction import DeltTransaction
from model.database.employee import Employee
from model.database.position_catalogue_record import PositionCatalogueRecord
from model.database.price_reset import PriceReset
from model.database.salary_payout import SalaryPayout
from model.database.tpay_transaction import TpayTransaction
from model.results.award_record import AwardRecord
from model.results.ltrans_result import LTransResult
from model.types.transaction_type import TransactionType
from repository.ordering_type import OrderingType
from resources.const import glob
from resources.sql import scripts


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


""" Insert """


async def insert_member(member: Member) -> None:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_MEMBER, (
            member.user_id,
            member.username,
            member.first_name,
            member.last_name,
            member.tickets
        ))
        await db.commit()


async def insert_addt(addt: AddtTransaction) -> None:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_ADDT, (
            addt.user_id,
            addt.tickets,
            addt.time,
            addt.description,
            addt.type_
        ))
        await db.commit()


async def insert_delt(delt: DeltTransaction) -> None:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_DELT, (
            delt.user_id,
            delt.tickets,
            delt.time,
            delt.description,
            delt.type_
        ))
        await db.commit()


async def insert_tpay(tpay: TpayTransaction):
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


async def insert_award(award: Award):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_AWARD, (
            award.award_id,
            award.name,
            award.description,
            award.payment
        ))
        await db.commit()


async def insert_award_member(am: AwardMemberJunction) -> bool:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        try:
            await db.execute(scripts.INSERT_AWARD_MEMBER, (
                am.award_id,
                am.owner_id,
                am.issue_date
            ))
            await db.commit()
            return True
        except IntegrityError:
            return False


async def insert_price_history(price_reset: PriceReset):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_PRICE_HISTORY, (
            price_reset.inflation,
            price_reset.fluctuation,
            price_reset.plan_date,
            price_reset.fact_date
        ))
        await db.commit()


async def insert_salary_payout(payout: SalaryPayout):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_SALARY_PAYOUT, (
            payout.plan_date,
            payout.fact_date,
            payout.paid_out
        ))
        await db.commit()


async def insert_employee(user_id: float, position: str, hired_date: str):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_EMPLOYEE, (
            user_id,
            position,
            hired_date
        ))
        await db.commit()


async def insert_employment_history(paid_member: Employee, fired_date: str):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_EMPLOYMENT_HISTORY, (
            paid_member.user_id,
            paid_member.position,
            paid_member.salary,
            paid_member.hired_date,
            fired_date
        ))
        await db.commit()


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


async def get_awards(user_id: int) -> Optional[List[AwardRecord]]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_AWARD_RECORDS_BY_OWNER_ID, (user_id,))
        rows = await cursor.fetchall()
        return [AwardRecord(Award(*row[:-1]), row[-1]) for row in rows]


async def get_awards_count(user_id: int) -> int:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_AWARDS_COUNT_BY_OWNER_ID, (user_id,))
        row = await cursor.fetchone()
        return int(row[0]) if row else 0


async def get_total_tickets(skip_negative: bool = True, time: datetime = None) -> float:
    total_query = f"{scripts.SELECT_TOTAL_TICKETS_COUNT} {'WHERE tickets > 0' if skip_negative else str()}"
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(total_query)
        row = await cursor.fetchone()
        cur_total = float(row[0]) if row else 0

    if time is not None:
        next_day = time + timedelta(days=1)
        next_day_datetime = datetime(next_day.year, next_day.month, next_day.day)
        async with aiosqlite.connect(glob.rms.db_file_path) as db:
            cursor = await db.execute(
                scripts.SELECT_DELTA_TICKETS_COUNT_AFTER_DATETIME,
                (next_day_datetime, next_day_datetime)
            )
            row = await cursor.fetchone()
            return cur_total if row[0] is None else cur_total - float(row[0])
    else:
        return cur_total


async def get_transaction_stats(user_id: int) -> LTransResult:
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

        return LTransResult(user_id, tpays, addts, delts, unique_tpay_members)


async def get_last_price_reset() -> Optional[PriceReset]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_PRICE_HISTORY)
        row = await cursor.fetchone()
        return PriceReset(*row) if row else None


async def get_last_salary_payout() -> Optional[SalaryPayout]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_SALARY_PAYOUT)
        row = await cursor.fetchone()
        return SalaryPayout(*row) if row else None


async def get_employees() -> Optional[List[Employee]]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_EMPLOYEES)
        rows = await cursor.fetchall()
        return [Employee(*row) for row in rows]


async def get_employee(user_id: float, position: str) -> Optional[Employee]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_EMPLOYEE_BY_PRIMARY_KEY, (user_id, position))
        row = await cursor.fetchone()
        return Employee(*row) if row else None


async def get_employee_position_names(user_id: float) -> Optional[List[str]]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_EMPLOYEE_POSITION_NAMES, (user_id,))
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


async def get_position_catalogue() -> Optional[List[PositionCatalogueRecord]]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_POSITION_CATALOGUE)
        rows = await cursor.fetchall()
        return [PositionCatalogueRecord(*row) for row in rows]


""" Update """


async def update_member_names(member: Member) -> None:
    await _execute(scripts.UPDATE_MEMBER_NAMES, (
        member.username,
        member.first_name,
        member.last_name,
        member.user_id
    ))


async def update_member_tickets(member: Member) -> None:
    await _execute(scripts.UPDATE_MEMBER_TICKETS, (
        member.tickets,
        member.user_id
    ))


async def spend_tpay_available(member: Member):
    await _execute(scripts.UPDATE_MEMBER_TPAY_AVAILABLE, (
        member.tpay_available - 1,
        member.user_id
    ))


async def set_salary_paid_out(plan_date: str, fact_date: str):
    await _execute(scripts.UPDATE_SALARY_PAYOUT, (
        1,
        fact_date,
        plan_date
    ))


""" Delete """


async def delete_employee(user_id: float, position: str):
    await _execute(scripts.DELETE_PAID_MEMBER, (
        user_id,
        position
    ))
