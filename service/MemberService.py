import copy
from typing import Union

from aiogram.types import Message, User

from model.database.Member import Member
from repository.MemberRepository import MemberRepository


class MemberService:
    def __init__(self, repository: MemberRepository):
        self.repo = repository

    async def create(self, value: Union[Member, User]) -> None:
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

    async def list(self) -> list[Member]:
        return await self.repo.list()

    async def validate_member(self, user: User) -> None:
        if await self.member_exists(user.id):
            await self.update_member_info(user)
        else:
            await self.create(user)

    async def member_exists(self, user_id: int) -> bool:
        return await self.repo.read(user_id) is not None

    async def update_member_info(self, user: User) -> None:
        old_member = await self.repo.read(user.id)
        updated_member = copy.deepcopy(old_member)
        changed = False

        if old_member.username != user.username:
            changed = True
            updated_member.set_username(user.username)

        print(f'old_member.first_name: {old_member.first_name}; user.first_name: {user.first_name}')
        if old_member.first_name != user.first_name:
            changed = True
            updated_member.set_first_name(user.first_name)

        if old_member.last_name != user.last_name:
            changed = True
            updated_member.set_last_name(user.last_name)

        if changed:
            await self.repo.update_names(updated_member)

    async def add_tickets(self, message: Message, tickets_to_add: int) -> None:
        user = message.reply_to_message.from_user
        await self.validate_member(user)

        cur_tickets_count = (await self.repo.read(user.id)).tickets_count

        member = Member(
            user_id=user.id,
            tickets_count=cur_tickets_count + tickets_to_add
        )

        await self.repo.update_tickets_count(member)

    async def get_balance(self, user: User) -> int:
        await self.validate_member(user)
        return (await self.repo.read(user.id)).tickets_count
