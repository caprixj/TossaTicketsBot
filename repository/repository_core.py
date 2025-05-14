from datetime import datetime
from sqlite3 import IntegrityError
from typing import Optional, List

import aiosqlite
from aiosqlite import Cursor

from model.database import (
    Artifact, Award, AwardMemberJunction, Member, AddtTransaction,
    DeltTransaction, Employee, Job, RateReset,
    SalaryPayout, TpayTransaction, Price, Ingredient
)
from model.database.transactions import BusinessProfitTransaction, MaterialTransaction
from model.dto import AwardDTO, LTransDTO
from model.types import TicketTransactionType
from repository.ordering_type import OrderingType
from resources.const import glob
from resources.const.glob import DATETIME_FORMAT
from resources.funcs.funcs import get_current_datetime
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
        unique_members.append(Member(*row) if row else Member(user_id=member_id, first_name='[deleted]'))

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


async def insert_member(member: Member):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_MEMBER, (
            member.user_id,
            member.username,
            member.first_name,
            member.last_name,
            member.tickets
        ))
        await db.commit()


async def insert_addt(addt: AddtTransaction):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_ADDT, (
            addt.user_id,
            addt.tickets,
            addt.time,
            addt.description,
            addt.type_
        ))
        await db.commit()


async def insert_delt(delt: DeltTransaction):
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


async def insert_business_profit(bpt: BusinessProfitTransaction):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_BUSINESS_PROFIT, (
            bpt.user_id,
            bpt.profit_type,
            bpt.transfer,
            bpt.date,
            bpt.artifact_id
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


async def insert_rate_history(price_reset: RateReset):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_RATE_HISTORY, (
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


async def insert_material_transaction(mt: MaterialTransaction):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_MATERIAL_TRANSACTION, (
            mt.sender_id,
            mt.receiver_id,
            mt.type_,
            mt.material_name,
            mt.quantity,
            mt.transfer,
            mt.tax,
            mt.date,
            mt.description
        ))
        await db.commit()


async def insert_daily_schedule(date: str):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(scripts.INSERT_DAILY_SCHEDULE, (date, ))
        await db.commit()


async def expand_price_history():
    price_history_data = [
        (p.product_name, p.product_type, p.price, get_current_datetime())
        for p in await get_prices()
    ]

    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.executemany(
            scripts.INSERT_PRICE_HISTORY,
            price_history_data
        )
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
        rows = await cursor.fetchall()
        return [Artifact(*row) for row in rows]


async def get_all_artifacts() -> List[Artifact]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_ARTIFACTS)
        rows = await cursor.fetchall()
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


async def get_awards(user_id: int) -> Optional[List[AwardDTO]]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_AWARD_RECORDS_BY_OWNER_ID, (user_id,))
        rows = await cursor.fetchall()
        return [AwardDTO(Award(*row[:-1]), row[-1]) for row in rows]


async def get_awards_count(user_id: int) -> int:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_AWARDS_COUNT_BY_OWNER_ID, (user_id,))
        row = await cursor.fetchone()
        return int(row[0]) if row else 0


async def get_nbt() -> float:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_SQL_VAR, (glob.NBT_SQL_VAR, ))
        row = await cursor.fetchone()
        return float(row[0]) if row else 0


async def get_sum_tickets() -> float:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_SUM_TICKETS)
        row = await cursor.fetchone()
        return float(row[0]) if row else 0


async def get_sum_business_accounts() -> float:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_SUM_BUSINESS_ACCOUNTS)
        row = await cursor.fetchone()
        return float(row[0]) if row else 0


async def get_transaction_stats(user_id: int) -> LTransDTO:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.cursor()

        # tpays
        await cursor.execute(scripts.SELECT_TPAY_BY_SENDER_OR_RECEIVER, (user_id, user_id))
        tpays = await cursor.fetchall()
        tpays = [TpayTransaction(*row) for row in tpays]

        # addts
        await cursor.execute(
            scripts.SELECT_ADDT_TYPE_NOT_TPAY,
            (user_id, TicketTransactionType.tpay, TicketTransactionType.tpay_tax)
        )
        addts = await cursor.fetchall()
        addts = [AddtTransaction(*row) for row in addts]

        # delts
        await cursor.execute(
            scripts.SELECT_DELT_TYPE_NOT_TPAY,
            (user_id, TicketTransactionType.tpay, TicketTransactionType.tpay_tax)
        )
        delts = await cursor.fetchall()
        delts = [DeltTransaction(*row) for row in delts]

        # unique_tpay_members
        unique_tpay_members = await _get_unique_members(cursor, user_id, tpays)

        return LTransDTO(user_id, tpays, addts, delts, unique_tpay_members)


async def get_last_daily_schedule_date() -> Optional[datetime]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_LAST_DAILY_SCHEDULE)
        row = await cursor.fetchone()
        return datetime.strptime(row[1], glob.DATETIME_FORMAT) if row else None


async def get_last_rate_history() -> Optional[RateReset]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_LAST_RATE_HISTORY)
        row = await cursor.fetchone()
        return RateReset(*row) if row else None


async def get_last_salary_payout() -> Optional[SalaryPayout]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_LAST_SALARY_PAYOUT)
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


async def get_jobs() -> Optional[List[Job]]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_JOBS)
        rows = await cursor.fetchall()
        return [Job(*row) for row in rows]


async def get_prices() -> List[Price]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_PRICES)
        rows = await cursor.fetchall()
        return [Price(*row) for row in rows]


async def get_gem_prices_dict() -> dict[str, float]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_GEM_PRICES)
        rows = await cursor.fetchall()
        return {r[0]: float(r[2]) for r in rows}


async def get_each_material_count() -> dict[str, int]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_EACH_MATERIAL_COUNT)
        rows = await cursor.fetchall()
        return {row[0]: row[1] for row in rows}


async def get_member_material(user_id: int, material_name: str) -> Optional[Ingredient]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_MEMBER_MATERIAL, (user_id, material_name))
        row = await cursor.fetchone()
        return Ingredient(*row) if row else None


async def get_all_member_materials(user_id: int) -> list[Ingredient]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_ALL_MEMBER_MATERIALS, (user_id,))
        rows = await cursor.fetchall()
        return [
            Ingredient(
                name=row[0],
                quantity=int(row[1])
            ) for row in rows
        ]


async def get_sold_items_count_today(user_id: int) -> int:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime(DATETIME_FORMAT)
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_SOLD_ITEMS_COUNT_TODAY, (user_id, today))
        row = await cursor.fetchone()
        return int(row[0]) if row[0] else 0


async def get_material_price(material_name: str) -> float:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(scripts.SELECT_GEMSTONE_PRICE, (material_name, ))
        row = await cursor.fetchone()
        return float(row[0]) if row else 0


""" Update """


async def update_member_names(member: Member):
    await _execute(scripts.UPDATE_MEMBER_NAMES, (
        member.username,
        member.first_name,
        member.last_name,
        member.user_id
    ))


async def update_member_tickets(member: Member):
    await _execute(scripts.UPDATE_MEMBER_TICKETS, (
        member.tickets,
        member.user_id
    ))


async def update_member_business_account(member: Member):
    await _execute(scripts.UPDATE_MEMBER_BUSINESS_ACCOUNT, (
        member.business_account,
        member.user_id
    ))


async def spend_tpay_available(user_id: int):
    await _execute(scripts.SPEND_MEMBER_TPAY_AVAILABLE, (user_id, ))


async def spend_tbox_available(user_id: int):
    await _execute(scripts.SPEND_MEMBER_TBOX_AVAILABLE, (user_id, ))


async def add_member_material(user_id: int, diff: Ingredient):
    mm = await get_member_material(user_id, diff.name)
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        if mm:
            await db.execute(scripts.ADD_MEMBER_MATERIAL, (
                diff.quantity,
                user_id,
                diff.name
            ))
        else:
            await db.execute(scripts.INSERT_MEMBER_MATERIAL, (
                user_id,
                diff.name,
                diff.quantity
            ))
        await db.commit()


async def spend_member_material(user_id: int, diff: Ingredient):
    mm = await get_member_material(user_id, diff.name)
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        if mm.quantity - diff.quantity > 0:
            await db.execute(scripts.SPEND_MEMBER_MATERIAL, (
                diff.quantity,
                user_id,
                diff.name
            ))
        else:
            await db.execute(scripts.DELETE_MEMBER_MATERIAL, (
                user_id,
                diff.name
            ))
        await db.commit()


async def set_salary_paid_out(plan_date: str, fact_date: str):
    await _execute(scripts.UPDATE_SALARY_PAYOUT, (
        1,
        fact_date,
        plan_date
    ))


async def reset_prices(diff: float):
    await _execute(scripts.RESET_PRICES, (diff,))


async def reset_gem_rate(name: str, price: float):
    await _execute(scripts.RESET_GEM_RATE, (price, name))


async def reset_artifact_investments(diff: float):
    await _execute(scripts.RESET_ARTIFACT_VALUES, (diff,))


""" Delete """


async def delete_employee(user_id: int, position: str):
    await _execute(scripts.DELETE_PAID_MEMBER, (
        user_id,
        position
    ))


async def delete_member(user_id: int):
    await _execute(scripts.DELETE_MEMBER, (user_id,))
