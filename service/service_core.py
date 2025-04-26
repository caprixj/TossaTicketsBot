import copy
from datetime import datetime
from typing import Union, Optional, List
from aiogram.types import User

import resources.const.glob as glob
from command.parser.results.parser_result import CommandParserResult
from command.parser.types.target_type import CommandTargetType as CTT

from model.database import EmployeeAssignment, EmploymentHistory, Member, AddtTransaction, DeltTransaction, \
    TpayTransaction, Award, AwardMember
from model.dto import AwardDTO, LTransDTO, TransactionResult
from model.types import TransactionResultErrors as TRE, TransactionType
from repository.ordering_type import OrderingType
from repository import repository_core as repo
from service.operation_manager import ServiceOperationManager
from resources.funcs.funcs import get_formatted_name, get_fee, get_current_datetime, date_to_str

operation_manager: ServiceOperationManager = ServiceOperationManager()


async def _add_tickets(member: Member, tickets: float, transaction_type: TransactionType, description: str = None):
    member.tickets += tickets
    time = get_current_datetime()

    await repo.update_member_tickets(member)
    await repo.insert_record(AddtTransaction(
        user_id=member.user_id,
        tickets=tickets,
        time=time,
        description=description,
        type_=transaction_type
    ))


async def _delete_tickets(member: Member, tickets: float, transaction_type: TransactionType, description: str = None):
    member.tickets -= tickets
    time = get_current_datetime()

    await repo.update_member_tickets(member)
    await repo.insert_record(DeltTransaction(
        user_id=member.user_id,
        tickets=tickets,
        time=time,
        description=description,
        type_=transaction_type
    ))


async def _set_tickets(member: Member, tickets: float, transaction_type: TransactionType, description: str = None):
    if member.tickets == tickets:
        return

    time = get_current_datetime()

    if tickets > member.tickets:
        await repo.insert_record(AddtTransaction(
            user_id=member.user_id,
            tickets=tickets - member.tickets,
            time=time,
            description=description,
            type_=transaction_type
        ))
    else:
        await repo.insert_record(DeltTransaction(
            user_id=member.user_id,
            tickets=member.tickets - tickets,
            time=time,
            description=description,
            type_=transaction_type
        ))

    member.tickets = tickets
    await repo.update_member_tickets(member)


async def execute_sql(query: str) -> (bool, str):
    return await repo.execute_external(query)


""" Interfaces """


async def topt(size: int = 0, percent: bool = False) -> str:
    sized = size != 0

    if sized:
        order = OrderingType.DESC if size > 0 else OrderingType.ASC
        members = await repo.get_members_by_tickets_limited(order, abs(size))
        result = f'{glob.TOPT_DESC if size > 0 else glob.TOPT_ASC}'
    else:
        order = str()
        members = await repo.get_members_by_tickets()
        result = f'{glob.TOPT_DESC} {glob.TOPT_FULL}'

    total_tickets = await repo.get_total_tickets(skip_negative=True)
    result += f"\n{glob.TOPT_TICKETS_TOTAL}: {total_tickets:.2f} tc\n\n"

    for i, m in enumerate(members):
        name = get_formatted_name(Member(
            username=m.username,
            first_name=m.first_name,
            last_name=m.last_name
        ))

        iterator = str()
        if i < 3 and (not sized or order == OrderingType.DESC):
            if i == 0:
                iterator = '🥇'
            elif i == 1:
                iterator = '🥈'
            elif i == 2:
                iterator = '🥉'
        else:
            iterator = f'{i + 1}.'

        if percent:
            value = f'{m.tickets / total_tickets * 100:.2f}%' \
                if m.tickets > 0 else glob.TOPT_BANKRUPT
        else:
            sign = '+' if m.tickets > 0 else str()
            value = f'{sign}{m.tickets:.2f}'

        result += f'{iterator} ( {value} )  {name[:32]}\n'

        if i == 2:
            result += '\n'

    return result


async def infm(user_id: int) -> str:
    member = await repo.get_member_by_user_id(user_id)

    positions = str()
    for pn in await get_position_names(user_id):
        positions += f'\n~ {pn}'

    return (f"{glob.INFM_TEXT}"
            f"\n\n<b>{glob.INFM_PERSONAL_INFO}</b>"
            f"\nid: {member.user_id}"
            f"\n{glob.INFM_FIRST_NAME}: {'-' if member.first_name is None else member.first_name}"
            f"\n{glob.INFM_LAST_NAME}: {'-' if member.last_name is None else member.last_name}"
            f"\n{glob.INFM_USERNAME}: {'-' if member.username is None else member.username}"
            f"\n\n<b>{glob.INFM_JOBS}</b>"
            f"{positions}"
            f"\n\n<b>{glob.INFM_COLLECTION}</b>"
            f"\n{glob.INFM_ARTIFACTS}: {await repo.get_artifacts_count(user_id)}"
            f"\n{glob.INFM_AWARDS}: {await repo.get_awards_count(user_id)}"
            f"\n\n<b>{glob.INFM_ASSETS}</b>"
            f"\n{glob.INFM_TICKETS}: {'+' if member.tickets > 0 else str()}{member.tickets:.2f}"
            f"\n{glob.INFM_TRANS_AVAILABLE}: {member.tpay_available}")


async def addt(member: Member, tickets: float, description: str = None) -> None:
    await _add_tickets(member, tickets, TransactionType.creator, description)


async def delt(member: Member, tickets: float, description: str = None) -> None:
    await _delete_tickets(member, tickets, TransactionType.creator, description)


async def sett(member: Member, tickets: float, description: str = None) -> None:
    await _set_tickets(member, tickets, TransactionType.creator, description)


async def tpay(sender: Member, receiver: Member, transfer: float, description: str = None) -> TransactionResult:
    fee = await get_fee(transfer)
    total = transfer + fee

    if total > sender.tickets:
        return TransactionResult(TRE.insufficient_funds)

    time = get_current_datetime()

    # sender: -transfer -tpay_available
    sender.tickets -= transfer
    await repo.update_member_tickets(sender)
    await repo.spend_tpay_available(sender)
    await repo.insert_record(DeltTransaction(
        user_id=sender.user_id,
        tickets=transfer,
        time=time,
        description=description,
        type_=TransactionType.tpay
    ))

    # sender: -fee
    sender.tickets -= fee
    await repo.update_member_tickets(sender)
    await repo.insert_record(DeltTransaction(
        user_id=sender.user_id,
        tickets=fee,
        time=time,
        description=description,
        type_=TransactionType.tpay_fee
    ))

    # receiver: +transfer
    receiver.tickets += transfer
    await repo.update_member_tickets(receiver)
    await repo.insert_record(AddtTransaction(
        user_id=receiver.user_id,
        tickets=transfer,
        time=time,
        description=description,
        type_=TransactionType.tpay
    ))

    # save tpay transaction
    await repo.insert_record(TpayTransaction(
        sender_id=sender.user_id,
        receiver_id=receiver.user_id,
        transfer=transfer,
        fee=fee,
        time=time,
        description=description
    ))

    return TransactionResult(valid=True)


async def ltrans(user_id: int) -> LTransDTO:
    return await repo.get_transaction_stats(user_id)


async def laward(user_id: int) -> Optional[List[AwardDTO]]:
    return await repo.get_awards(user_id)


async def issue_award(am: AwardMember) -> bool:
    return await repo.insert_record(am)


async def pay_award(member: Member, payment: float, description: str):
    await _add_tickets(member, payment, TransactionType.award, description)


async def hire(user_id: float, position: str):
    await repo.insert_record(
        EmployeeAssignment(
            user_id=user_id,
            position=position,
            hired_date=get_current_datetime()
        )
    )


async def fire(user_id: float, position: str) -> bool:
    employee = await repo.get_employee(user_id, position)

    if employee is None:
        return False
    else:
        await repo.insert_record(
            EmploymentHistory(
                user_id=user_id,
                position=position,
                hired_date=employee.hired_date,
                fired_date=get_current_datetime()
            )
        )
        await repo.delete_employee(user_id, position)
        return True


""" Get """


async def get_member(user_id: int) -> Optional[Member]:
    return await repo.get_member_by_user_id(user_id)


async def get_target_member(cpr: CommandParserResult) -> Optional[Member]:
    if cpr.overload.target_type == CTT.none:
        user_id = cpr.message.from_user.id
        return await repo.get_member_by_user_id(user_id)
    elif cpr.overload.target_type == CTT.reply:
        user_id = cpr.message.reply_to_message.from_user.id
        return await repo.get_member_by_user_id(user_id)
    elif cpr.overload.target_type == CTT.username:
        return await repo.get_member_by_username(cpr.args[glob.USERNAME_ARG])
    elif cpr.overload.target_type == CTT.user_id:
        return await repo.get_member_by_user_id(cpr.args[glob.USER_ID_ARG])


async def get_award(cpr: CommandParserResult) -> Optional[Award]:
    return await repo.get_award(cpr.args[glob.AWARD_ID_ARG])


""" Member """


async def create_member(value: Union[Member, User]) -> None:
    if isinstance(value, Member):
        await repo.insert_record(value)
    elif isinstance(value, User):
        member = Member(
            user_id=value.id,
            username=value.username,
            first_name=value.first_name,
            last_name=value.last_name
        )
        await repo.insert_record(member)
    else:
        raise TypeError()


async def update_member(user: User, member: Member = None):
    if member is None:
        member = await repo.get_member_by_user_id(user.id)

    updated_member = copy.deepcopy(member)
    changed = False

    if member.username != user.username:
        changed = True
        updated_member.username = user.username

    if member.first_name != user.first_name:
        changed = True
        updated_member.first_name = user.first_name

    if member.last_name != user.last_name:
        changed = True
        updated_member.last_name = user.last_name

    if changed:
        await repo.update_member_names(updated_member)


""" Other """


async def reset_tpay_available() -> (bool, str):
    return await repo.reset_tpay_available()


async def payout_salaries(lsp_plan_date: datetime):
    employees = await repo.get_employees()

    if employees is None:
        await repo.set_salary_paid_out(
            plan_date=date_to_str(lsp_plan_date),
            fact_date=date_to_str(datetime.now())
        )
        return

    for e in employees:
        if e.salary != 0:
            await _add_tickets(
                member=await repo.get_member_by_user_id(e.user_id),
                tickets=e.salary,
                transaction_type=TransactionType.salary,
                description=TransactionType.salary
            )

    await repo.set_salary_paid_out(
        plan_date=date_to_str(lsp_plan_date),
        fact_date=date_to_str(datetime.now())
    )


async def is_hired(user_id: float, position: str) -> bool:
    return await repo.get_employee(user_id, position) is not None


async def get_position_names(user_id: float) -> Optional[List[str]]:
    return await repo.get_employee_position_names(user_id)
