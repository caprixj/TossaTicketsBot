from typing import Optional

from model.Member import Member
from repository.MemberRepository import MemberRepository


class MemberService:
    def __init__(self, repository: MemberRepository):
        self.repo = repository

    #################################### !!!
    async def reset_dp_path(self, db_path: str) -> None:
        self.repo.db_path = db_path

    # Repository methods
    async def create(self, member: Member) -> None:
        await self.repo.create(member)

    async def read(self, user_id: int) -> Optional[Member]:
        return await self.repo.read(user_id)

    async def delete(self, user_id: int) -> None:
        await self.repo.delete(user_id)

    async def update_names(self, user_id: int, username: str, first_name: str, last_name: str) -> None:
        member = Member(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        await self.repo.update_names(member)

    async def update_tickets_count(self, tickets_count: int) -> None:
        member = Member(tickets_count=tickets_count)
        await self.repo.update_tickets_count(member)

    async def update_unique_artifacts(self, unique_artifacts: list[int]) -> None:
        member = Member(unique_artifacts=unique_artifacts)
        await self.repo.update_unique_artifacts(member)

    async def list(self) -> list[Member]:
        return await self.repo.list()

    # Service methods
    async def user_exists(self, user_id: int) -> bool:
        return await self.read(user_id) is not None

