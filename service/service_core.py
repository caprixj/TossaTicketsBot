import copy
from typing import Union, Optional

from aiogram import Bot
from aiogram.types import User

import utilities.glob as glob
from comparser.parser_result import CommandParserResult
from comparser.types.target_type import CommandTargetType as ctt
from model.database.award import Award
from model.database.member import Member
from model.database.transactions.addt_transaction import AddtTransaction
from model.database.transactions.delt_transaction import DeltTransaction
from model.database.transactions.tpay_transaction import TpayTransaction
from model.database.transactions.tr_messages import TransactionResultErrors as trm
from model.database.transactions.transaction_result import TransactionResult
from model.database.transactions.transaction_type import TransactionType
from repository.ordering_type import OrderingType
from repository.repository_core import Repository
from service.service_operation_manager import ServiceOperationManager
from utilities.funcs import get_formatted_name, get_fee, get_transaction_time
from utilities.sql_scripts import RESET_TPAY_AVAILABLE


class Service:
    def __init__(self, db_file_path: str = None):
        self.repo = Repository(db_file_path) if db_file_path else None
        self.bot: Optional[Bot] = None
        self.operation_manager = ServiceOperationManager()

    async def execute_sql(self, query: str) -> (bool, str):
        return await self.repo.execute_external(query)

    """ Functional """

    # async def _get_artifact_names(self, user_id: int) -> str:
    #     arl = str()
    #     for ar in await self.repo.get_artifact_names(user_id):
    #         arl += f'«{ar}», '
    #
    #     return arl[:-2] if arl else '-'

    async def _add_tickets(self, member: Member, tickets: float, transaction_type: TransactionType,
                           description: str = None) -> None:
        member.tickets += tickets
        time = get_transaction_time()

        await self.repo.update_member_tickets(member)
        await self.repo.create_stat_addt(AddtTransaction(
            user_id=member.user_id,
            tickets=tickets,
            time=time,
            description=description,
            type_=transaction_type
        ))

    async def _delete_tickets(self, member: Member, tickets: float, transaction_type: TransactionType,
                              description: str = None) -> None:
        member.tickets -= tickets
        time = get_transaction_time()

        await self.repo.update_member_tickets(member)
        await self.repo.create_stat_delt(DeltTransaction(
            user_id=member.user_id,
            tickets=tickets,
            time=time,
            description=description,
            type_=transaction_type
        ))

    async def _set_tickets(self, member: Member, tickets: float, transaction_type: TransactionType,
                           description: str = None) -> None:
        if member.tickets == tickets:
            return

        time = get_transaction_time()

        if tickets > member.tickets:
            await self.repo.create_stat_addt(AddtTransaction(
                user_id=member.user_id,
                tickets=tickets - member.tickets,
                time=time,
                description=description,
                type_=transaction_type
            ))
        else:
            await self.repo.create_stat_delt(DeltTransaction(
                user_id=member.user_id,
                tickets=member.tickets - tickets,
                time=time,
                description=description,
                type_=transaction_type
            ))

        member.tickets = tickets
        await self.repo.update_member_tickets(member)

    """ Interfaces """

    async def topt(self) -> str:
        result = f'{glob.TOPT_DESC} (повний)\n\n'
        members = await self.repo.get_members_by_tickets()

        for i, m in enumerate(members):
            name = await get_formatted_name(Member(
                username=m.username,
                first_name=m.first_name,
                last_name=m.last_name
            ))

            iterator = str()
            if i < 3:
                if i == 0:
                    iterator = '🥇'
                elif i == 1:
                    iterator = '🥈'
                elif i == 2:
                    iterator = '🥉'
            else:
                iterator = f'{i + 1}.'

            sign = '+' if m.tickets > 0 else str()
            result += f'{iterator} ( {sign}{m.tickets:.2f} )  {name[:32]}\n'

            if i == 2:
                result += '\n'

        return result

    async def topt_sized(self, size: int) -> str:
        result = f'{glob.TOPT_DESC if size > 0 else glob.TOPT_ASC}\n\n'
        order = OrderingType.DESC if size > 0 else OrderingType.ASC
        members = await self.repo.get_members_by_tickets_limited(order, abs(size))

        for i, m in enumerate(members):
            name = await get_formatted_name(Member(
                username=m.username,
                first_name=m.first_name,
                last_name=m.last_name
            ))

            iterator = str()
            if i < 3 and order == OrderingType.DESC:
                if i == 0:
                    iterator = '🥇'
                elif i == 1:
                    iterator = '🥈'
                elif i == 2:
                    iterator = '🥉'
            else:
                iterator = f'{i + 1}.'

            sign = '+' if m.tickets > 0 else str()
            result += f'{iterator} ( {sign}{m.tickets:.2f} )  {name[:32]}\n'

            if i == 2:
                result += '\n'

        return result

    async def infm(self, user_id: int) -> str:
        member = await self.repo.get_member_by_user_id(user_id)

        return (f"{glob.INFM_TEXT}"
                f"\n\n<b>🪪 персональні дані</b>"
                f"\nid: {member.user_id}"
                f"\nім'я: {'-' if member.first_name is None else member.first_name}"
                f"\nпрізвище: {'-' if member.last_name is None else member.last_name}"
                f"\nюзернейм: {'-' if member.username is None else member.username}"
                f"\n\n<b>💎 колекція</b>"
                f"\nартефактів: {await self.repo.get_artifacts_count(user_id)}"
                f"\nнагород: {await self.repo.get_awards_count(user_id)}"
                f"\n\n<b>💳 активи</b>"
                f"\nтікети: {'+' if member.tickets > 0 else str()}{member.tickets:.2f}"
                f"\nдоступно транзакцій: {member.tpay_available}")

    async def addt(self, member: Member, tickets: float, description: str = None) -> None:
        await self._add_tickets(member, tickets, TransactionType.creator, description)

    async def delt(self, member: Member, tickets: float, description: str = None) -> None:
        await self._delete_tickets(member, tickets, TransactionType.creator, description)

    async def sett(self, member: Member, tickets: float, description: str = None) -> None:
        await self._set_tickets(member, tickets, TransactionType.creator, description)

    async def tpay(self, sender: Member, receiver: Member, transfer: float,
                   description: str = None) -> TransactionResult:
        fee = await get_fee(transfer)
        total = transfer + fee

        if total > sender.tickets:
            return TransactionResult(trm.insufficient_funds)

        time = get_transaction_time()

        # sender: -transfer -tpay_available
        sender.tickets -= transfer
        await self.repo.update_member_tickets(sender)
        await self.repo.spend_tpay_available(sender)
        await self.repo.create_stat_delt(DeltTransaction(
            user_id=sender.user_id,
            tickets=transfer,
            time=time,
            description=description,
            type_=TransactionType.tpay
        ))

        # sender: -fee
        sender.tickets -= fee
        await self.repo.update_member_tickets(sender)
        await self.repo.create_stat_delt(DeltTransaction(
            user_id=sender.user_id,
            tickets=fee,
            time=time,
            description=description,
            type_=TransactionType.tpay_fee
        ))

        # receiver: +transfer
        receiver.tickets += transfer
        await self.repo.update_member_tickets(receiver)
        await self.repo.create_stat_addt(AddtTransaction(
            user_id=receiver.user_id,
            tickets=transfer,
            time=time,
            description=description,
            type_=TransactionType.tpay
        ))

        # save tpay transaction
        await self.repo.create_stat_tpay(TpayTransaction(
            sender_id=sender.user_id,
            receiver_id=receiver.user_id,
            transfer=transfer,
            fee=fee,
            time=time,
            description=description
        ))

        return TransactionResult(valid=True)

    async def issue_award(self, award: Award, member: Member) -> bool:
        return await self.repo.create_award_member(award, member)

    async def pay_award(self, member: Member, payment: float):
        await self._add_tickets(member, payment, TransactionType.award)

    """ Get """

    async def get_member(self, user_id: int) -> Optional[Member]:
        return await self.repo.get_member_by_user_id(user_id)

    async def get_target_member(self, cpr: CommandParserResult) -> Optional[Member]:
        if cpr.overload.target_type == ctt.none:
            user_id = cpr.message.from_user.id
            return await self.repo.get_member_by_user_id(user_id)
        elif cpr.overload.target_type == ctt.reply:
            user_id = cpr.message.reply_to_message.from_user.id
            return await self.repo.get_member_by_user_id(user_id)
        elif cpr.overload.target_type == ctt.username:
            return await self.repo.get_member_by_username(cpr.args[glob.USERNAME_ARG])
        elif cpr.overload.target_type == ctt.user_id:
            return await self.repo.get_member_by_user_id(cpr.args[glob.USER_ID_ARG])

    async def get_award(self, cpr: CommandParserResult) -> Optional[Award]:
        return await self.repo.get_award(cpr.args[glob.AWARD_ID_ARG])

    async def get_award_issue_date(self, user_id: int) -> str:
        return await self.repo.get_award_addt_time(user_id)

    """ Member """

    async def create_member(self, value: Union[Member, User]) -> None:
        if isinstance(value, Member):
            await self.repo.create_member(value)
        elif isinstance(value, User):
            member = Member(
                user_id=value.id,
                username=value.username,
                first_name=value.first_name,
                last_name=value.last_name
            )
            await self.repo.create_member(member)
        else:
            raise TypeError()

    async def update_member(self, user: User, member: Member = None):
        if member is None:
            member = await self.repo.get_member_by_user_id(user.id)

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
            await self.repo.update_member_names(updated_member)

    """ Other """

    async def reset_tpay_available(self) -> (bool, str):
        return await self.repo.execute_external(RESET_TPAY_AVAILABLE)
