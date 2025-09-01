from datetime import datetime, timezone
from sqlite3 import IntegrityError
from typing import Optional, List

import aiosqlite
from aiosqlite import Cursor

from model.database import *
from model.database.transactions import BusinessProfitTransaction, MaterialTransaction, TicketTransaction, \
    TaxTransaction
from model.dto import AwardDTO, LTransDTO
from model.types import TicketTxnType
from repository.ordering_type import OrderingType
from resources.funcs import utcnow_str
from resources import glob, funcs
from repository import sql


async def sql_execute(query: str, many: bool = False) -> (bool, str):
    try:
        async with aiosqlite.connect(glob.rms.db_file_path) as db:
            await db.execute('begin')
            results = []

            if not many:
                success, response = await _execute_external(query, db)
            else:
                queries = [q.strip() for q in query.split(';') if q.strip()]
                for q in queries:
                    results.append(await _execute_external(q, db))

                success = all(r[0] for r in results)
                response = '\n\n'.join(f'{i + 1} >\n{r[1]}' for i, r in enumerate(results))

            response = response if len(response) <= glob.TG_MSG_LEN_LIMIT \
                else glob.TG_MSG_LEN_LIMIT_ERROR

            if success:
                await db.commit()
                return True, response
            else:
                await db.rollback()
                return False, response

    except Exception as e:
        return False, str(e)


async def _execute_external(query: str, db) -> (bool, str):
    try:
        async with db.cursor() as cursor:
            await cursor.execute(query)

            if query.strip().lower().startswith('select'):
                rows = await cursor.fetchall()
                result = '\n'.join(' | '.join(str(f) for f in r) for r in rows)
            else:
                result = str(cursor.rowcount)

            if len(result) > glob.TG_MSG_LEN_LIMIT:
                return False, glob.TG_MSG_LEN_LIMIT_ERROR
            return True, result

    except Exception as e:
        return False, str(e)


async def _execute(query: str, params: tuple = ()):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor


""" Insert """


async def insert_member(m: Member):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(sql.INSERT_MEMBER, (
            m.user_id,
            m.username,
            m.first_name,
            m.last_name,
            m.tickets,
            m.anchor
        ))
        await db.commit()


async def insert_del_member(dm: DelMember):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(sql.INSERT_DEL_MEMBER, (
            dm.user_id,
            dm.username,
            dm.first_name,
            dm.last_name,
            dm.anchor
        ))
        await db.commit()


async def insert_ticket_txn(ticket_txn: TicketTransaction) -> int:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.INSERT_TICKET_TXN, (
            ticket_txn.sender_id,
            ticket_txn.receiver_id,
            ticket_txn.transfer,
            ticket_txn.type,
            funcs.to_iso_z(ticket_txn.time),
            ticket_txn.description
        ))
        row = await cursor.fetchone()
        await db.commit()
        return int(row[0]) if row else 0


async def insert_tax_txn(tax_txn: TaxTransaction) -> int:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.INSERT_TAX_TXN, (
            tax_txn.parent_id,
            tax_txn.user_id,
            tax_txn.amount,
            tax_txn.tax_type,
            tax_txn.parent_type,
            funcs.to_iso_z(tax_txn.time)
        ))
        row = await cursor.fetchone()
        await db.commit()
        return int(row[0]) if row else 0


async def insert_business_profit(bpt: BusinessProfitTransaction):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(sql.INSERT_BUSINESS_PROFIT, (
            bpt.user_id,
            bpt.profit_type,
            bpt.transfer,
            funcs.to_iso_z(bpt.date),
            bpt.artifact_id
        ))
        await db.commit()


async def insert_award(award: Award):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(sql.INSERT_AWARD, (
            award.award_id,
            award.name,
            award.description,
            award.payment
        ))
        await db.commit()


async def insert_award_member(am: AwardMember) -> bool:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        try:
            await db.execute(sql.INSERT_AWARD_MEMBER, (
                am.award_id,
                am.owner_id,
                funcs.to_iso_z(am.issue_date)
            ))
            await db.commit()
            return True
        except IntegrityError:
            return False


async def insert_rate_history(price_reset: RateReset):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(sql.INSERT_RATE_HISTORY, (
            price_reset.inflation,
            price_reset.fluctuation,
            funcs.to_iso_z(price_reset.plan_date),
            funcs.to_iso_z(price_reset.fact_date)
        ))
        await db.commit()


async def insert_salary_payout(payout: SalaryPayout):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        fact_date = None if not payout.fact_date else funcs.to_iso_z(payout.fact_date)
        await db.execute(sql.INSERT_SALARY_PAYOUT, (
            funcs.to_iso_z(payout.plan_date),
            fact_date,
            payout.paid_out
        ))
        await db.commit()


async def insert_employee(user_id: int, position: str, hired_date: str):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(sql.INSERT_EMPLOYEE, (
            user_id,
            position,
            hired_date
        ))
        await db.commit()


async def insert_employment_history(paid_member: Employee, fired_date: str):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(sql.INSERT_EMPLOYMENT_HISTORY, (
            paid_member.user_id,
            paid_member.position,
            paid_member.salary,
            funcs.to_iso_z(paid_member.hired_date),
            fired_date
        ))
        await db.commit()


async def insert_material_transaction(mt: MaterialTransaction):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(sql.INSERT_MAT_TXNS, (
            mt.sender_id,
            mt.receiver_id,
            mt.type_,
            mt.material_name,
            mt.quantity,
            mt.ticket_txn,
            funcs.to_iso_z(mt.date),
            mt.description
        ))
        await db.commit()


async def insert_daily_schedule(date: str):
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.execute(sql.INSERT_DAILY_SCHEDULE, (date,))
        await db.commit()


async def expand_price_history():
    price_history_data = [
        (p.product_name, p.product_type, p.price, utcnow_str())
        for p in await get_prices()
    ]

    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        await db.executemany(
            sql.INSERT_PRICE_HISTORY,
            price_history_data
        )
        await db.commit()


""" Read """


async def get_member_by_user_id(user_id: int) -> Optional[Member]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_MEMBER_BY_USER_ID, (user_id,))
        row = await cursor.fetchone()
        return Member(*row) if row else None


async def get_del_member_by_user_id(user_id: int) -> Optional[DelMember]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_DEL_MEMBER_BY_USER_ID, (user_id,))
        row = await cursor.fetchone()
        return DelMember(*row) if row else None


async def get_member_by_username(username: str) -> Optional[Member]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_MEMBER_BY_USERNAME, (username,))
        row = await cursor.fetchone()
        return Member(*row) if row else None


async def get_topt_members(order: OrderingType = OrderingType.DESC, limit: Optional[int] = None) -> list[Member]:
    limit_clause = 'LIMIT ?' if limit is not None else ''
    query = sql.SELECT_TOPT.format(
        order=order.value,
        limit_clause=limit_clause
    )
    params = (limit,) if limit is not None else ()

    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()

    return [Member(*row) for row in rows]


async def get_artifacts(user_id: int) -> List[Artifact]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_ARTIFACTS_BY_OWNER_ID, (user_id,))
        rows = await cursor.fetchall()
        return [Artifact(*row) for row in rows]


async def get_all_artifacts() -> List[Artifact]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_ARTIFACTS)
        rows = await cursor.fetchall()
        return [Artifact(*row) for row in rows]


async def get_artifacts_count(user_id: int) -> int:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_ARTIFACTS_COUNT_BY_OWNER_ID, (user_id,))
        row = await cursor.fetchone()
        return int(row[0]) if row else 0


async def get_award(award_id: str) -> Optional[Award]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_AWARD, (award_id,))
        row = await cursor.fetchone()
        return Award(*row) if row else None


async def get_awards(user_id: int) -> Optional[List[AwardDTO]]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_AWARD_RECORDS_BY_OWNER_ID, (user_id,))
        rows = await cursor.fetchall()
        return [AwardDTO(Award(*row[:-1]), row[-1]) for row in rows]


async def get_awards_count(user_id: int) -> int:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_AWARDS_COUNT_BY_OWNER_ID, (user_id,))
        row = await cursor.fetchone()
        return int(row[0]) if row else 0


async def get_nbt() -> int:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_SQL_VAR, (glob.NBT_SQL_VAR,))
        row = await cursor.fetchone()
        return int(row[0]) if row else 0


async def get_sum_tickets() -> int:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_SUM_TICKETS)
        row = await cursor.fetchone()
        return int(row[0]) if row else 0


async def get_sum_business_accounts() -> int:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_SUM_BUSINESS_ACCOUNTS)
        row = await cursor.fetchone()
        return int(row[0]) if row else 0


async def get_txn_stats(user_id: int) -> LTransDTO:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.cursor()

        # tpays
        await cursor.execute(
            sql.SELECT_TPAYS_AND_TAXATION_BY_USER_ID,
            (user_id, user_id)
        )
        # transaction details: affiliated taxes sum
        tpays = {TicketTransaction(*row[:-1]): row[-1] for row in await cursor.fetchall()}

        # addts
        await cursor.execute(
            sql.SELECT_ADDTS_BY_USER_ID,
            (user_id, TicketTxnType.CREATOR)
        )
        addts = [TicketTransaction(*row) for row in await cursor.fetchall()]

        # delts
        await cursor.execute(
            sql.SELECT_DELTS_BY_USER_ID,
            (user_id, TicketTxnType.CREATOR)
        )
        delts = [TicketTransaction(*row) for row in await cursor.fetchall()]

        # msells
        await cursor.execute(
            sql.SELECT_MSELLS_BY_USER_ID,
            (user_id, TicketTxnType.MSELL)
        )
        msells = [TicketTransaction(*row) for row in await cursor.fetchall()]

        # salaries
        await cursor.execute(
            sql.SELECT_SALARY_TXNS_BY_USER_ID,
            (user_id, TicketTxnType.SALARY)
        )
        salaries = [TicketTransaction(*row) for row in await cursor.fetchall()]

        # awards
        await cursor.execute(
            sql.SELECT_AWARD_TXNS_BY_USER_ID,
            (user_id, TicketTxnType.AWARD)
        )
        awards_ = [TicketTransaction(*row) for row in await cursor.fetchall()]

        # unknown
        await cursor.execute(
            sql.SELECT_UNKNOWN_TXNS_BY_USER_ID,
            (user_id, TicketTxnType.UNKNOWN)
        )
        unknowns = [TicketTransaction(*row) for row in await cursor.fetchall()]

        # taxes (tpay single tax excluded)
        await cursor.execute(
            sql.SELECT_NON_TPAY_TAXES_BY_USER_ID,
            (user_id,)
        )
        taxes = [TaxTransaction(*row) for row in await cursor.fetchall()]

        # unique_tpay_members
        unique_tpay_members = await _get_unique_members(cursor, user_id, tpays)

        return LTransDTO(
            user_id,
            tpays,
            addts,
            delts,
            msells,
            salaries,
            awards_,
            unknowns,
            taxes,
            unique_tpay_members
        )


async def get_last_daily_schedule_date() -> Optional[datetime]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_LAST_DAILY_SCHEDULE)
        row = await cursor.fetchone()
        return funcs.to_utc(row[1]) if row else None


async def get_last_rate_history() -> Optional[RateReset]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_LAST_RATE_HISTORY)
        row = await cursor.fetchone()
        return RateReset(*row) if row else None


async def get_last_salary_payout() -> Optional[SalaryPayout]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_LAST_SALARY_PAYOUT)
        row = await cursor.fetchone()
        return SalaryPayout(*row) if row else None


async def get_employees() -> Optional[List[Employee]]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_EMPLOYEES)
        rows = await cursor.fetchall()
        return [Employee(*row) for row in rows]


async def get_employee(user_id: int, position: str) -> Optional[Employee]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_EMPLOYEE_BY_PRIMARY_KEY, (user_id, position))
        row = await cursor.fetchone()
        return Employee(*row) if row else None


async def get_job_names(user_id: int) -> Optional[List[str]]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_EMPLOYEE_JOB_NAMES, (user_id,))
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


async def get_job_name(position: str) -> Optional[str]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_JOB_NAME, (position,))
        row = await cursor.fetchone()
        return row[0] if row else None


async def get_jobs() -> Optional[List[Job]]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_JOBS)
        rows = await cursor.fetchall()
        return [Job(*row) for row in rows]


async def get_prices() -> List[Price]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_PRICES)
        rows = await cursor.fetchall()
        return [Price(*row) for row in rows]


async def get_gem_rates_dict() -> dict[str, float]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_GEM_RATES)
        rows = await cursor.fetchall()
        return {r[0]: float(r[2]) for r in rows}


async def get_each_material_count() -> list[Ingredient]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_EACH_MATERIAL_COUNT)
        rows = await cursor.fetchall()
        return [
            Ingredient(
                name=row[0],
                quantity=int(row[1])
            ) for row in rows
        ]


async def get_member_material(user_id: int, material_name: str) -> Optional[Ingredient]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_MEMBER_MATERIAL, (user_id, material_name))
        row = await cursor.fetchone()
        return Ingredient(*row) if row else None


async def get_member_materials_by_user_id(user_id: int) -> list[Ingredient]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_MEMBER_MATERIALS_BY_USER_ID, (user_id,))
        rows = await cursor.fetchall()
        return [
            Ingredient(
                name=row[0],
                quantity=int(row[1])
            ) for row in rows
        ]


async def get_all_member_materials() -> list[MemberMaterial]:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_ALL_MEMBER_MATERIALS)
        rows = await cursor.fetchall()
        return [MemberMaterial(*row) for row in rows]


async def get_member_sold_mc_by_period(user_id: int) -> int:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(
            sql.SELECT_MEMBER_SOLD_MAT_COUNT_BY_PERIOD,
            (user_id, datetime.now(timezone.utc).strftime(glob.DATE_FORMAT))
        )
        row = await cursor.fetchone()
        return int(row[0]) if row[0] else 0


async def get_sold_mat_revenue_by_period(start_day: datetime) -> int:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(
            sql.SELECT_SOLD_MAT_REVENUE_BY_PERIOD,
            (start_day.strftime(glob.DATE_FORMAT),)
        )
        row = await cursor.fetchone()
        return int(row[0]) if row[0] else 0


async def get_farmed_mc_by_period(start_day: datetime) -> int:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(
            sql.SELECT_FARMED_MAT_COUNT_BY_PERIOD,
            (start_day.strftime(glob.DATE_FORMAT),)
        )
        row = await cursor.fetchone()
        return int(row[0]) if row[0] else 0


async def get_material_price(material_name: str) -> float:
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        cursor = await db.execute(sql.SELECT_GEMSTONE_PRICE, (material_name,))
        row = await cursor.fetchone()
        return float(row[0]) if row else 0


async def _get_unique_members(cursor: Cursor, user_id: int, tpays: dict[TicketTransaction, int]) -> list[Member]:
    unique_ids = set()
    unique_members = list()

    for tt in tpays:
        if tt.sender_id != user_id:
            unique_ids.add(tt.sender_id)
        if tt.receiver_id != user_id:
            unique_ids.add(tt.receiver_id)

    for member_id in unique_ids:
        await cursor.execute(sql.SELECT_MEMBER_BY_USER_ID, (member_id,))
        row = await cursor.fetchone()
        unique_members.append(
            Member(*row) if row else Member(
                user_id=member_id,
                first_name=glob.DELETED_MEMBER
            )
        )

    return unique_members


""" Update """


async def update_member_names(m: Member):
    await _execute(sql.UPDATE_MEMBER_NAMES, (
        m.username,
        m.first_name,
        m.last_name,
        m.user_id
    ))


async def update_member_tickets(m: Member):
    await _execute(sql.UPDATE_MEMBER_TICKETS, (
        m.tickets,
        m.user_id
    ))


async def update_member_business_account(m: Member):
    await _execute(sql.UPDATE_MEMBER_BUSINESS_ACCOUNT, (
        m.business_account,
        m.user_id
    ))


async def update_member_anchor(m: Member):
    await _execute(sql.UPDATE_MEMBER_ANCHOR, (
        m.anchor,
        m.user_id
    ))


async def spend_tpay_available(user_id: int):
    await _execute(sql.SPEND_MEMBER_TPAY_AVAILABLE, (user_id,))


async def spend_tbox_available(user_id: int):
    await _execute(sql.SPEND_MEMBER_TBOX_AVAILABLE, (user_id,))


async def reset_tpay_available():
    await _execute(sql.RESET_MEMBER_TPAY_AVAILABLE, (glob.TPAY_AVAILABLE_LIMIT,))


async def reset_tbox_available():
    await _execute(sql.RESET_MEMBER_TBOX_AVAILABLE)


async def add_member_material(user_id: int, diff: Ingredient):
    mm = await get_member_material(user_id, diff.name)
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        if mm:
            await db.execute(sql.ADD_MEMBER_MATERIAL, (
                diff.quantity,
                user_id,
                diff.name
            ))
        else:
            await db.execute(sql.INSERT_MEMBER_MATERIAL, (
                user_id,
                diff.name,
                diff.quantity
            ))
        await db.commit()


async def spend_member_material(user_id: int, diff: Ingredient):
    mm = await get_member_material(user_id, diff.name)
    async with aiosqlite.connect(glob.rms.db_file_path) as db:
        if mm.quantity - diff.quantity > 0:
            await db.execute(sql.SPEND_MEMBER_MATERIAL, (
                diff.quantity,
                user_id,
                diff.name
            ))
        else:
            await db.execute(sql.DELETE_MEMBER_MATERIAL, (
                user_id,
                diff.name
            ))
        await db.commit()


async def set_salary_paid_out(plan_date: str, fact_date: str):
    await _execute(sql.UPDATE_SALARY_PAYOUT, (
        1,
        fact_date,
        plan_date
    ))


async def reset_prices(diff: float):
    await _execute(sql.RESET_PRICES, (diff,))


async def reset_gem_rate(name: str, price: float):
    await _execute(sql.RESET_GEM_RATE, (price, name))


async def reset_artifact_investments(diff: float):
    await _execute(sql.RESET_ARTIFACT_VALUES, (diff,))


""" Delete """


async def delete_employee(user_id: int, position: str):
    await _execute(sql.DELETE_PAID_MEMBER, (
        user_id,
        position
    ))


async def delete_member(user_id: int):
    await _execute(sql.DELETE_MEMBER, (user_id,))


async def delete_del_member(user_id: int):
    await _execute(sql.DELETE_DEL_MEMBER, (user_id,))
