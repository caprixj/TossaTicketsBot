import copy
import utilities.globals as glob
import comparser.standard_overloads as sol

from datetime import datetime
from typing import Union, Optional

from aiogram.types import User

from model.database.Member import Member
from model.database.transactions.AddtTransaction import AddtTransaction
from model.database.transactions.DeltTransaction import DeltTransaction
from comparser.enums.OverloadType import OverloadType as cot
from comparser.results import CommandParserResult
from utilities.func import get_formatted_name
from repository.OrderingType import OrderingType
from repository.Repository import Repository


async def _get_transaction_time() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class Service:
    def __init__(self, repository: Repository = None):
        self.repo = repository
        self.bot = None

    async def execute_sql(self, query: str) -> (bool, str):
        # (!) NO member validation is held
        return await self.repo.execute_external(query)

    async def validate_member(self, user: User) -> None:
        if await self._member_exists_by_user_id(user.id):
            await self._update_member_info(user)
        else:
            await self._create(user)

    async def get_member_tickets_count_info(self, member: Member) -> str:
        name = await get_formatted_name(
            user_id=member.user_id,
            username=member.username,
            first_name=member.first_name,
            last_name=member.last_name,
            ping=True
        )

        sign = '+' if member.tickets_count > 0 else str()
        arl = await self._get_artifact_names_by_user_id_str(member.user_id)

        return f"🪪 ім'я: {name}\n💳 тікети: {sign}{member.tickets_count}\n🔮 артефакти: {arl}"

    async def add_tickets(self, member: Member, tickets_count: int, description: str = None) -> None:
        member.tickets_count += tickets_count
        transaction_time = await _get_transaction_time()

        await self.repo.update_tickets_count(member)
        await self.repo.add_stat_addt(AddtTransaction(
            user_id=member.user_id,
            tickets_count=tickets_count,
            transaction_time=transaction_time,
            description=description
        ))

    async def delete_tickets(self, member: Member, tickets_count: int, description: str = None) -> None:
        member.tickets_count -= tickets_count
        transaction_time = await _get_transaction_time()

        await self.repo.update_tickets_count(member)
        await self.repo.add_stat_delt(DeltTransaction(
            user_id=member.user_id,
            tickets_count=tickets_count,
            transaction_time=transaction_time,
            description=description
        ))

    async def set_tickets(self, member: Member, tickets_count: int, description: str = None) -> None:
        if member.tickets_count == tickets_count:
            return

        transaction_time = await _get_transaction_time()

        if tickets_count > member.tickets_count:
            await self.repo.add_stat_addt(AddtTransaction(
                user_id=member.user_id,
                tickets_count=tickets_count - member.tickets_count,
                transaction_time=transaction_time,
                description=description
            ))
        else:
            await self.repo.add_stat_delt(DeltTransaction(
                user_id=member.user_id,
                tickets_count=member.tickets_count - tickets_count,
                transaction_time=transaction_time,
                description=description
            ))

        member.tickets_count = tickets_count
        await self.repo.update_tickets_count(member)

    async def get_tickets_top(self) -> str:
        result = f'{glob.TOPT_DESC_TEXT} (повний)\n\n'
        members = await self.repo.get_members_by_tickets()

        for i, m in enumerate(members):
            name = await get_formatted_name(
                username=m.username,
                first_name=m.first_name,
                last_name=m.last_name
            )

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

            sign = '+' if m.tickets_count > 0 else str()
            result += f'{iterator} ( {sign}{m.tickets_count} )  {name[:32]}\n'

            if i == 2:
                result += '\n'

        return result

    async def get_tickets_top_by_size(self, size: int) -> str:
        result = f'{glob.TOPT_DESC_TEXT if size > 0 else glob.TOPT_ASC_TEXT}\n\n'
        order = OrderingType.DESC if size > 0 else OrderingType.ASC
        members = await self.repo.get_members_by_tickets_limited(order, abs(size))

        for i, m in enumerate(members):
            name = await get_formatted_name(
                username=m.username,
                first_name=m.first_name,
                last_name=m.last_name
            )

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

            sign = '+' if m.tickets_count > 0 else str()
            result += f'{iterator} ( {sign}{m.tickets_count} )  {name[:32]}\n'

            if i == 2:
                result += '\n'

        return result

    async def get_member_info(self, user_id: int) -> str:
        member = await self.repo.read_by_user_id(user_id)

        fn = member.first_name
        ln = member.last_name
        un = member.username
        tc = member.tickets_count
        arl = await self._get_artifact_names_by_user_id_str(user_id)
        sign = '+' if tc > 0 else str()

        return (f"{glob.INFM_TEXT}\n"
                f"\nід: {member.user_id}"
                f"\nім'я: {'-' if fn is None else fn}"
                f"\nпрізвище: {'-' if ln is None else ln}"
                f"\nюзернейм: {'-' if un is None else un}"
                f"\n\n<b>💳 активи</b>"
                f"\nтікети: {sign}{tc}"
                f"\nартефакти: {arl}")

    async def get_member_by_cpr(self, cpr: CommandParserResult, user: User) -> Optional[Member]:
        if cpr.overload.type == cot.reply:
            await self.validate_member(user)
            return await self.repo.read_by_user_id(user.id)
        elif cpr.overload.type == cot.username:
            return await self.repo.read_by_username(cpr.params.get(sol.USERNAME))
        elif cpr.overload.type == cot.user_id:
            return await self.repo.read_by_user_id(cpr.params.get(sol.USER_ID))

    async def _create(self, value: Union[Member, User]) -> None:
        if isinstance(value, Member):
            await self.repo.create(value)

        elif isinstance(value, User):
            member = Member(
                user_id=value.id,
                username=value.username,
                first_name=value.first_name,
                last_name=value.last_name
            )
            await self.repo.create(member)

        else:
            raise TypeError("Invalid argument type")

    async def _member_exists_by_user_id(self, user_id: int) -> bool:
        return await self.repo.read_by_user_id(user_id) is not None

    async def _member_exists_by_username(self, username: str) -> bool:
        return await self.repo.read_by_username(username) is not None

    async def _update_member_info(self, user: User) -> None:
        old_member = await self.repo.read_by_user_id(user.id)
        updated_member = copy.deepcopy(old_member)
        changed = False

        if old_member.username != user.username:
            changed = True
            updated_member.username = user.username

        if old_member.first_name != user.first_name:
            changed = True
            updated_member.first_name = user.first_name

        if old_member.last_name != user.last_name:
            changed = True
            updated_member.last_name = user.last_name

        if changed:
            await self.repo.update_names(updated_member)

    async def _get_artifact_names_by_user_id_str(self, user_id: int) -> str:
        arl = str()
        for ar in await self.repo.get_artifact_names_by_user_id(user_id):
            arl += f'«{ar}», '

        return arl[:-2] if arl else '-'
