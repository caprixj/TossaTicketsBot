from datetime import datetime
from math import ceil
from typing import List, Tuple

from model.database.member import Member
from model.results.mytpay_result import MytpayResult
from resources.funcs.funcs import get_formatted_name
from resources.const.glob import PAGE_ROW_CHAR_LIMIT, PAGE_ROWS_COUNT_LIMIT


def _sorted_by_datetime(rows: List[Tuple[str, datetime]]) -> List[str]:
    rows.sort(key=lambda x: x[1], reverse=True)
    return [row for row, time in rows]


def _find_member(members: List[Member], user_id: int) -> Member:
    for m in members:
        if m.user_id == user_id:
            return m

    raise RuntimeError('member not found in unique_tpay_members')


def _form_pages(title: str, rows: List[str]) -> List[str]:
    pages = []
    cur_page = []
    cur_page_size = 0

    for row in rows:
        row_size = 1 + ceil(len(row) / PAGE_ROW_CHAR_LIMIT)

        if cur_page_size + row_size <= PAGE_ROWS_COUNT_LIMIT:
            cur_page.append(row)
            cur_page_size += row_size
        else:
            pages.append('\n\n'.join([title, *cur_page]))
            cur_page = [row]
            cur_page_size = row_size

    if cur_page:
        pages.append('\n\n'.join([title, *cur_page]))

    return pages


async def mytpay(result: MytpayResult, title: str) -> List[str]:
    rows = []

    for addt in result.addts:
        row = (f"✨🔹 | id: {addt.addt_id}"
               f" | <b>+{addt.tickets:.2f}</b>"
               f" | {addt.time}"
               f" | опис: <i>{addt.description}</i>")
        rows.append((row, addt.time))

    for delt in result.delts:
        row = (f"✨🔻 | id: {delt.delt_id}"
               f" | <b>-{delt.tickets:.2f}</b>"
               f" | {delt.time}"
               f" | опис: <i>{delt.description}</i>")
        rows.append((row, delt.time))

    for tpay in result.tpays:
        if tpay.receiver_id == result.user_id:
            sender_name = get_formatted_name(_find_member(result.unique_tpay_members, tpay.sender_id))
            row = (f"🔀🔹 | id: {tpay.tpay_id}"
                   f" | від: <b>{sender_name}</b>"
                   f" | <b>+{tpay.transfer:.2f}</b>"
                   f" | {tpay.time}"
                   f" | опис: <i>{tpay.description}</i>")
        else:
            receiver_name = get_formatted_name(_find_member(result.unique_tpay_members, tpay.receiver_id))
            row = (f"🔀🔻 | id: {tpay.tpay_id}"
                   f" | кому: <b>{receiver_name}</b>"
                   f" | <b>-{tpay.transfer:.2f}</b>"
                   f" | -{tpay.fee:.2f}"
                   f" | {tpay.time}"
                   f" | опис: <i>{tpay.description}</i>")

        rows.append((row, tpay.time))

    return _form_pages(title, _sorted_by_datetime(rows))
