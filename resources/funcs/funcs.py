from datetime import datetime

from model.database.member import Member
from resources.const.glob import FEE_RATE as F, MIN_FEE as M, DATETIME_FORMAT


def get_current_datetime() -> str:
    return datetime.now().strftime(DATETIME_FORMAT)


def date_to_str(date: datetime) -> str:
    return date.strftime(DATETIME_FORMAT)


async def get_fee(transfer: float) -> float:
    return max(round(F * transfer, 2), M)


async def get_transfer_by_total(t: float) -> float:
    return t - M if F * (t - M) <= M else round(t / (F + 1), 2)


def get_formatted_name(member: Member, ping: bool = False) -> str:
    name = str()

    if member.first_name or member.last_name:
        fn_not_empty = False
        if member.first_name:
            fn_not_empty = True
            name += member.first_name
        if member.last_name:
            name += ' ' if fn_not_empty else str()
            name += member.last_name
    elif member.username:
        name += member.username
    else:
        name = '-'

    name.replace('[', '(')
    name.replace(']', ')')

    return name if not ping else \
        f'@{name}' if name == member.username else f'[{name}](tg://user?id={member.user_id})'
