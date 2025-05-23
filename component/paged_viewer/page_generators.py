from datetime import datetime
from math import ceil
from typing import Optional

from service import service_core as service
from model.database import Ingredient
from model.database.member import Member
from model.dto.award_dto import AwardDTO
from model.dto.ltrans_dto import LTransDTO
from resources.const import glob
from resources.funcs.funcs import get_formatted_name
from resources.const.glob import PAGE_ROW_CHAR_LIMIT, PAGE_ROWS_COUNT_LIMIT


async def balm(data: list[Ingredient], title: str) -> list[str]:
    if not data:
        return [f'{title}\n\n<i>{glob.BALM_BALANCE_EMPTY}</i>']

    # dict[str, int]
    gemstones_rows = {}
    intermediates_rows = {}
    artifact_templates_rows = {}

    for ing in data:
        row = (f'{ing.quantity}{await service.get_emoji(ing.name)} '
               f'({await service.get_formatted_material_name(ing.name)})\n')
        if await service.is_gem(ing.name):
            gemstones_rows[row] = ing.quantity
        elif await service.is_intermediate(ing.name):
            intermediates_rows[row] = ing.quantity
        elif await service.is_artifact_template(ing.name):
            artifact_templates_rows[row] = ing.quantity

    def _form_page(rows: dict[str, int]) -> str:
        return ''.join(sorted(rows, key=rows.get, reverse=True))

    gemstones_page = _form_page(gemstones_rows)
    intermediates_page = _form_page(intermediates_rows)
    artifact_templates_page = _form_page(artifact_templates_rows)

    if not gemstones_page:
        gemstones_page = f'<i>{glob.BALM_NO_GEMSTONES}</i>'
    if not intermediates_page:
        intermediates_page = f'<i>{glob.BALM_NO_INTERMEDIATES}</i>'
    if not artifact_templates_page:
        artifact_templates_page = f'<i>{glob.BALM_NO_ARTIFACT_TEMPLATES}</i>'

    return [
        '\n\n'.join([title, page]) for page
        in [gemstones_page, intermediates_page, artifact_templates_page]
    ]


async def ltrans(dto: LTransDTO, title: str) -> list[str]:
    rows = []

    if dto.empty():
        return [f'{title}\n\n<i>{glob.LTRANS_TRANS_HISTORY_EMPTY}</i>']

    for addt in dto.addts:
        row = (f"✨🔹 | id: {addt.addt_id}"
               f" | <b>+{addt.tickets:.2f}</b>"
               f" | {addt.time}"
               f" | {glob.LTRANS_TEXT}: <i>{addt.description}</i>")
        rows.append((row, addt.time))

    for delt in dto.delts:
        row = (f"✨🔻 | id: {delt.delt_id}"
               f" | <b>-{delt.tickets:.2f}</b>"
               f" | {delt.time}"
               f" | {glob.LTRANS_TEXT}: <i>{delt.description}</i>")
        rows.append((row, delt.time))

    for tpay in dto.tpays:
        if tpay.receiver_id == dto.user_id:
            member = _find_member(dto.unique_tpay_members, tpay.sender_id)
            sender_name = get_formatted_name(member) if member is not None else glob.DELETED_MEMBER
            row = (f"🔀🔹 | id: {tpay.tpay_id}"
                   f" | {glob.LTRANS_FROM}: <b>{sender_name}</b>"
                   f" | <b>+{tpay.transfer:.2f}</b>"
                   f" | {tpay.time}"
                   f" | {glob.LTRANS_TEXT}: <i>{tpay.description}</i>")
        else:
            member = _find_member(dto.unique_tpay_members, tpay.receiver_id)
            receiver_name = get_formatted_name(member) if member is not None else glob.DELETED_MEMBER
            row = (f"🔀🔻 | id: {tpay.tpay_id}"
                   f" | {glob.LTRANS_TO}: <b>{receiver_name}</b>"
                   f" | <b>-{tpay.transfer:.2f}</b>"
                   f" | -{tpay.fee:.2f}"
                   f" | {tpay.time}"
                   f" | {glob.LTRANS_TEXT}: <i>{tpay.description}</i>")

        rows.append((row, tpay.time))

    pages = []
    cur_page = []
    cur_page_size = 0
    sorted_rows = _sorted_by_datetime(rows)

    for row in sorted_rows:
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


async def laward(result: list[AwardDTO], title: str) -> list[str]:
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


def _sorted_by_datetime(rows: list[tuple[str, datetime]]) -> list[str]:
    rows.sort(key=lambda x: x[1], reverse=True)
    return [row for row, time in rows]


def _find_member(members: list[Member], user_id: int) -> Optional[Member]:
    for m in members:
        if m.user_id == user_id:
            return m
