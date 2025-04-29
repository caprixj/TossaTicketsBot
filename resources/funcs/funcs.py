import re
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
    parts = [member.first_name or '', member.last_name or '']
    name = str(' '.join(filter(None, parts)) or member.username or '-')

    return f"[{_escape_brackets(name)}](tg://user?id={member.user_id})" \
        if ping else _escape_markdown_v2(name)


def _escape_markdown_v2(text: str) -> str:
    return re.sub(r'([_*])', r'\\\1', text)


def _escape_brackets(text: str) -> str:
    return text.replace('[', ' ').replace(']', ' ')
