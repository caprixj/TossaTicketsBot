from datetime import datetime
from math import ceil
from typing import List, Tuple

from model.database import Member
from model.dto import AwardDTO, LTransDTO
from resources.const import glob
from resources.funcs.funcs import get_formatted_name
from resources.const.glob import PAGE_ROW_CHAR_LIMIT, PAGE_ROWS_COUNT_LIMIT


async def ltrans(result: LTransDTO, title: str) -> List[str]:
    rows = []

    if result.empty():
        return [f'{title}\n\n<i>{glob.LTRANS_TRANS_HISTORY_EMPTY}</i>']

    for addt in result.addts:
        row = (f"✨🔹 | id: {addt.addt_id}"
               f" | <b>+{addt.tickets:.2f}</b>"
               f" | {addt.time}"
               f" | {glob.LTRANS_TEXT}: <i>{addt.description}</i>")
        rows.append((row, addt.time))

    for delt in result.delts:
        row = (f"✨🔻 | id: {delt.delt_id}"
               f" | <b>-{delt.tickets:.2f}</b>"
               f" | {delt.time}"
               f" | {glob.LTRANS_TEXT}: <i>{delt.description}</i>")
        rows.append((row, delt.time))

    for tpay in result.tpays:
        if tpay.receiver_id == result.user_id:
            sender_name = get_formatted_name(_find_member(result.unique_tpay_members, tpay.sender_id))
            row = (f"🔀🔹 | id: {tpay.tpay_id}"
                   f" | {glob.LTRANS_FROM}: <b>{sender_name}</b>"
                   f" | <b>+{tpay.transfer:.2f}</b>"
                   f" | {tpay.time}"
                   f" | {glob.LTRANS_TEXT}: <i>{tpay.description}</i>")
        else:
            receiver_name = get_formatted_name(_find_member(result.unique_tpay_members, tpay.receiver_id))
            row = (f"🔀🔻 | id: {tpay.tpay_id}"
                   f" | {glob.LTRANS_TO}: <b>{receiver_name}</b>"
                   f" | <b>-{tpay.transfer:.2f}</b>"
                   f" | -{tpay.fee:.2f}"
                   f" | {tpay.time}"
                   f" | {glob.LTRANS_TEXT}: <i>{tpay.description}</i>")

        rows.append((row, tpay.time))

    return _form_pages(title, _sorted_by_datetime(rows))


async def laward(result: List[AwardDTO], title: str) -> List[str]:
    pages = []
    first_page = str()

    if not result:
        return [f'{title}\n\n<i>{glob.PAGE_GEN_NO_AWARDS}</i>']

    first_page += f'<i>{glob.PAGE_GEN_AWARDS}: {len(result)}</i>\n'
    for ar in result:
        first_page += f'\n🎖 {ar.award.name}'

    pages.append('\n'.join([title, first_page]))

    for ar in result:
        award_text = (f"<b>🎖 {ar.award.name}</b>"
                      f"\n\nid: <b>{ar.award.award_id}</b>"
                      f"\n{glob.PAGE_GEN_PAYMENT}: <b>{ar.award.payment:.2f} tc</b>"
                      f"\n{glob.PAGE_GEN_ISSUED}: <b>{ar.issue_date}</b>"
                      f"\n\n<b>{glob.PAGE_GEN_STORY}</b>: <i>{ar.award.description}</i>")

        pages.append('\n\n'.join([title, award_text]))

    return pages


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
