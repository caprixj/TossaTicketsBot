from datetime import datetime, timedelta
from sqlite3 import IntegrityError
from typing import Optional

from sqlalchemy import (
    select, update, delete, func, or_, not_, union_all, literal, text, Executable
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce

from model.database import (
    Member, AddtTransaction, DeltTransaction, Artifact,
    Award, AwardMember, TpayTransaction,
    PriceReset, SalaryPayout, PositionCatalogueRecord,
    EmployeeAssignment
)
from model.dto import AwardDTO, LTransDTO
from model.types import TransactionType
from repository.session import get_async_session
from repository.ordering_type import OrderingType

AsyncSessionLocal = get_async_session()


async def _get_unique_members(session: AsyncSession, user_id: int, tpays: list[TpayTransaction]) -> list[Member]:
    unique_ids = {
        tt.sender_id for tt in tpays if tt.sender_id != user_id
    } | {
        tt.receiver_id for tt in tpays if tt.receiver_id != user_id
    }

    if not unique_ids:
        return []

    result = await session.execute(
        select(Member).where(Member.user_id.in_(unique_ids))
    )

    return list(result.scalars().all())


""" Execute """


async def _execute(statement: Executable):
    async with AsyncSessionLocal() as session:
        await session.execute(statement)
        await session.commit()


async def execute_external(query: str) -> (bool, str):
    try:
        async with AsyncSessionLocal() as session:
            stmt = text(query)
            res = await session.execute(stmt)

            if query.strip().lower().startswith('select'):
                rows = res.fetchall()
                out = "\n".join(
                    " | ".join(str(col) for col in row)
                    for row in rows
                )
            else:
                await session.commit()
                out = str(res.rowcount)

        return True, out

    except Exception as e:
        return False, str(e)


""" Insert """


async def insert_record(obj) -> bool:
    async with AsyncSessionLocal() as session:
        try:
            session.add(obj)
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            return False


""" Read """


async def get_member_by_user_id(user_id: int) -> Optional[Member]:
    async with AsyncSessionLocal() as session:
        return await session.get(Member, user_id)


async def get_member_by_username(username: str) -> Optional[Member]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Member).where(Member.username == username)
        )
        return result.scalars().first()


async def get_members_by_tickets() -> list[Member]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Member)
            .outerjoin(AddtTransaction)
            .outerjoin(DeltTransaction)
            .group_by(Member.user_id)
            .order_by(
                Member.tickets.desc(),
                func.max(coalesce(
                    AddtTransaction.time, DeltTransaction.time
                )).desc()
            )
        )
        return result.scalars().all()


async def get_members_by_tickets_limited(order: OrderingType, size: int) -> list[Member]:
    direction = Member.tickets.desc() if order == OrderingType.DESC else Member.tickets.asc()

    if order == OrderingType.DESC:
        time_dir = func.max(coalesce(AddtTransaction.time, DeltTransaction.time)).desc()
    else:
        time_dir = func.max(coalesce(AddtTransaction.time, DeltTransaction.time)).asc()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Member)
            .outerjoin(AddtTransaction)
            .outerjoin(DeltTransaction)
            .group_by(Member.user_id)
            .order_by(direction, time_dir)
            .limit(size)
        )

        return result.scalars().all()


async def get_artifacts(user_id: int) -> list[Artifact]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Artifact).where(Artifact.owner_id == user_id)
        )
        return result.scalars().all()


async def get_artifacts_count(user_id: int) -> int:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(func.count(Artifact.artifact_id))
            .where(Artifact.owner_id == user_id)
        )
        return result.scalar_one()


async def get_award(award_id: str) -> Optional[Award]:
    async with AsyncSessionLocal() as session:
        return await session.get(Award, award_id)


async def get_awards(user_id: int) -> list[AwardDTO]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Award, AwardMember.issue_date)
            .join(AwardMember)
            .where(AwardMember.owner_id == user_id)
            .order_by(AwardMember.issue_date.asc())
        )
        return [AwardDTO(row[0], row[1]) for row in result.all()]


async def get_awards_count(user_id: int) -> int:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(func.count(AwardMember.award_id))
            .where(AwardMember.owner_id == user_id)
        )
        return int(result.scalar() or 0)


async def get_total_tickets(skip_negative: bool = True, time: datetime = None) -> float:
    async with AsyncSessionLocal() as session:
        # total across all members (optionally skip negatives)
        stmt_total = (
            select(func.sum(Member.tickets))
            .where(Member.tickets > 0)
            if skip_negative
            else select(func.sum(Member.tickets))
        )
        result = await session.execute(stmt_total)
        cur_total = result.scalar() or 0.

        # if no cutoff time, return immediately
        if time is None:
            return cur_total

        # compute midnight of the next day
        next_day = time + timedelta(days=1)
        cutoff = datetime(next_day.year, next_day.month, next_day.day)

        # build two subqueries: addt and delt since cutoff
        add_subq = (
            select(
                func.date(AddtTransaction.time).label('date'),
                func.sum(AddtTransaction.tickets).label('add_sum'),
                literal(0).label('delt_sum')
            )
            .where(AddtTransaction.time >= cutoff)
            .group_by(func.date(AddtTransaction.time))
        )

        delt_subq = (
            select(
                func.date(DeltTransaction.time).label('date'),
                literal(0).label('add_sum'),
                func.sum(DeltTransaction.tickets).label('delt_sum')
            )
            .where(DeltTransaction.time >= cutoff)
            .group_by(func.date(DeltTransaction.time))
        )

        # union them and sum the delta per day
        union_q = union_all(add_subq, delt_subq).subquery()
        stmt_delta = select(func.sum(union_q.c.add_sum - union_q.c.delt_sum))

        delta_result = await session.execute(stmt_delta)
        delta_sum = delta_result.scalar()  # None if no rows

        # subtract if there was any delta
        if delta_sum is None:
            return cur_total

        return cur_total - float(delta_sum)


async def get_transaction_stats(user_id: int) -> LTransDTO:
    async with AsyncSessionLocal() as session:
        # tpay
        result = await session.execute(
            select(TpayTransaction)
            .where(
                or_(
                    TpayTransaction.sender_id == user_id,
                    TpayTransaction.receiver_id == user_id
                )
            )
        )
        tpays = list(result.scalars().all())

        # addt
        result = await session.execute(
            select(AddtTransaction)
            .where(
                AddtTransaction.user_id == user_id,
                not_(AddtTransaction.type_.in_([
                    TransactionType.tpay, TransactionType.tpay_fee
                ]))
            )
        )
        addts = list(result.scalars().all())

        # delt
        result = await session.execute(
            select(DeltTransaction)
            .where(
                DeltTransaction.user_id == user_id,
                not_(DeltTransaction.type_.in_([
                    TransactionType.tpay, TransactionType.tpay_fee
                ]))
            )
        )
        delts = list(result.scalars().all())

        # unique_tpay_members
        unique_tpay_members = await _get_unique_members(session, user_id, tpays)

        return LTransDTO(user_id, tpays, addts, delts, unique_tpay_members)


async def get_last_price_reset() -> Optional[PriceReset]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PriceReset)
            .order_by(PriceReset.plan_date.desc())
            .limit(1)
        )
        return result.scalars().first()


async def get_last_salary_payout() -> Optional[SalaryPayout]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SalaryPayout)
            .order_by(SalaryPayout.plan_date.desc())
            .limit(1)
        )
        return result.scalars().first()


async def get_employees() -> Optional[list[EmployeeAssignment]]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(
                EmployeeAssignment.user_id,
                EmployeeAssignment.position,
                PositionCatalogueRecord.salary,
                EmployeeAssignment.hired_date
            )
            .join(PositionCatalogueRecord)
        )
        return result.all()


async def get_employee(user_id: float, position: str) -> Optional[EmployeeAssignment]:
    async with AsyncSessionLocal() as session:
        return await session.get(EmployeeAssignment, (user_id, position))


async def get_employee_position_names(user_id: float) -> Optional[list[str]]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PositionCatalogueRecord.name_uk)
            .join(EmployeeAssignment)
            .where(EmployeeAssignment.user_id == user_id)
        )
        # (?!) return [r[0] for r in result.all()]
        return result.scalars().all()


async def get_position_catalogue() -> Optional[list[PositionCatalogueRecord]]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PositionCatalogueRecord)
        )
        return result.scalars().all()


""" Update """


async def update_member_names(member: Member):
    await _execute(
        update(Member)
        .where(Member.user_id == member.user_id)  # type: ignore
        .values(
            username=member.username,
            first_name=member.first_name,
            last_name=member.last_name
        )
    )


async def update_member_tickets(member: Member):
    await _execute(
        update(Member)
        .where(Member.user_id == member.user_id)  # type: ignore
        .values(tickets=member.tickets)
    )


async def spend_tpay_available(member: Member):
    await _execute(
        update(Member)
        .where(Member.user_id == member.user_id)  # type: ignore
        .values(tpay_available=member.tpay_available - 1)
    )


async def set_salary_paid_out(plan_date: str, fact_date: str):
    await _execute(
        update(SalaryPayout)
        .where(SalaryPayout.plan_date == plan_date)
        .values(
            paid_out=1,
            fact_date=fact_date
        )
    )


async def reset_tpay_available():
    await _execute(
        update(Member).values(tpay_available=3)
    )


""" Delete """


async def delete_employee(user_id: float, position: str):
    await _execute(
        delete(EmployeeAssignment)
        .where(
            EmployeeAssignment.user_id == user_id,
            EmployeeAssignment.position == position
        )
    )
