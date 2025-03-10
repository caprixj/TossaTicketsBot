import copy
from datetime import datetime
from typing import Union

from aiogram.types import User

from model.database.Member import Member
from model.database.transactions.AddtTransaction import AddtTransaction
from model.database.transactions.DeltTransaction import DeltTransaction
from utilities.func import get_formatted_name
from utilities.globalvars import GlobalVariables as GV
from repository.OrderingType import OrderingType
from repository.Repository import Repository


class Service:
    def __init__(self, repository: Repository = None):
        self.repo = repository

    async def execute_sql(self, query: str) -> (bool, str):
        # (!) NO member validation is held
        return await self.repo.execute_external(query)

    async def get_member_tickets_count_info(self, user: User) -> str:
        await self._validate_member(user)

        tickets_count = await self.repo.get_member_tickets_count(user.id)
        name = await get_formatted_name(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            ping=True
        )

        sign = '+' if tickets_count > 0 else str()
        return f"ім'я: {name}\n{GV.MEMBER_TICKETS_COUNT_TEXT}: {sign}{tickets_count}"

    async def add_tickets(self, user: User, tickets_count: int, description: str = None) -> None:
        await self._validate_member(user)

        cur_tickets_count = await self.repo.get_member_tickets_count(user.id)
        transaction_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        await self.repo.update_tickets_count(Member(
            user_id=user.id,
            tickets_count=cur_tickets_count + tickets_count
        ))
        await self.repo.add_stat_addt(AddtTransaction(
            user_id=user.id,
            tickets_count=tickets_count,
            transaction_time=transaction_time,
            description=description
        ))

    async def remove_tickets(self, user: User, tickets_count: int, description: str = None) -> None:
        await self._validate_member(user)

        cur_tickets_count = await self.repo.get_member_tickets_count(user.id)
        transaction_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        await self.repo.update_tickets_count(Member(
            user_id=user.id,
            tickets_count=cur_tickets_count - tickets_count
        ))
        await self.repo.add_stat_delt(DeltTransaction(
            user_id=user.id,
            tickets_count=tickets_count,
            transaction_time=transaction_time,
            description=description
        ))

    async def set_tickets(self, user: User, tickets_count: int, description: str = None) -> None:
        await self._validate_member(user)

        cur_tickets_count = await self.repo.get_member_tickets_count(user.id)
        transaction_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if cur_tickets_count == tickets_count:
            return

        await self.repo.update_tickets_count(Member(
            user_id=user.id,
            tickets_count=tickets_count
        ))

        if tickets_count > cur_tickets_count:
            await self.repo.add_stat_addt(AddtTransaction(
                user_id=user.id,
                tickets_count=tickets_count - cur_tickets_count,
                transaction_time=transaction_time,
                description=description
            ))
        else:
            await self.repo.add_stat_delt(DeltTransaction(
                user_id=user.id,
                tickets_count=cur_tickets_count - tickets_count,
                transaction_time=transaction_time,
                description=description
            ))

    async def get_members_top_on_tickets_count(self, user: User, top_size: int) -> str:
        await self._validate_member(user)

        result = f'{GV.TOPT_DESC_TEXT if top_size > 0 else GV.TOPT_ASC_TEXT}\n\n'
        order = OrderingType.DESC if top_size > 0 else OrderingType.ASC
        members = await self.repo.get_members_by_tickets_count(abs(top_size), order)

        for i in range(len(members)):
            m = members[i]
            name = await get_formatted_name(
                username=m.username,
                first_name=m.first_name,
                last_name=m.last_name
            )

            iterator = str()
            if i < 3 and order == OrderingType.DESC:
                if (i + 1) == 1:
                    iterator = '🥇'
                elif (i + 1) == 2:
                    iterator = '🥈'
                elif (i + 1) == 3:
                    iterator = '🥉'
            else:
                iterator = f'{i + 1}.'

            sign = '+' if m.tickets_count > 0 else str()
            result += f'{iterator} ( {sign}{m.tickets_count} )  {name[:32]}\n'

            if i == 2:
                result += '\n'

        return result

    async def get_member_info(self, user: User) -> str:
        await self._validate_member(user)
        member = await self.repo.read(user.id)

        fn = member.get_first_name()
        ln = member.get_last_name()
        un = member.get_username()
        tc = member.get_tickets_count()

        arl = str()
        for ar in await self.repo.get_artifact_names_by_user_id(user.id):
            arl += f'«{ar}», '
        arl = arl[:-2]

        sign = '+' if tc > 0 else str()

        return (f"{GV.MEMBER_INFO_TEXT}\n"
                f"\nайді: {member.get_id()}"
                f"\nім'я: {'-' if fn is None else fn}"
                f"\nпрізвище: {'-' if ln is None else ln}"
                f"\nюзернейм: {'-' if un is None else un}"
                f"\n\nособистий рахунок"
                f"\nтікети: {sign}{tc}"
                f"\nартефакти: {arl}")

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

    async def _validate_member(self, user: User) -> None:
        if await self._member_exists(user.id):
            await self._update_member_info(user)
        else:
            await self._create(user)

    async def _member_exists(self, user_id: int) -> bool:
        return await self.repo.read(user_id) is not None

    async def _update_member_info(self, user: User) -> None:
        old_member = await self.repo.read(user.id)
        updated_member = copy.deepcopy(old_member)
        changed = False

        if old_member.username != user.username:
            changed = True
            updated_member.set_username(user.username)

        if old_member.first_name != user.first_name:
            changed = True
            updated_member.set_first_name(user.first_name)

        if old_member.last_name != user.last_name:
            changed = True
            updated_member.set_last_name(user.last_name)

        if changed:
            await self.repo.update_names(updated_member)
