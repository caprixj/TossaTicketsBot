from datetime import datetime
from math import ceil
from typing import Optional

from service import service_core as service
from model.database.materials import Ingredient
from model.database.member import Member
from model.dto.award_dto import AwardDTO
from model.dto.ltrans_dto import TxnDTO
from resources import glob
from utils import funcs
from utils.funcs import get_formatted_name
from resources.glob import PAGE_ROW_CHAR_LIMIT, PAGE_ROWS_COUNT_LIMIT


async def balm(data: tuple[int, list[Ingredient]], title: str) -> list[str]:
    user_id: int = data[0]
    mat_data: list[Ingredient] = data[1]

    if not mat_data:
        return [f'{title}\n\n<i>{glob.BALM_BALANCE_EMPTY}</i>']

    # dict[str, int]
    gemstones_rows = {}
    intermediates_rows = {}
    artifact_templates_rows = {}

    for mat in mat_data:
        reserved = await service.get_material_reservation(user_id, mat.name)
        reserved_str = f' (-{reserved})' if reserved > 0 else ''

        emoji = await service.get_emoji(mat.name)
        material_name = await service.get_formatted_material_name(mat.name)

        row = f'{mat.quantity}{reserved_str}{emoji} ({material_name})\n'

        if await service.is_gem(mat.name):
            gemstones_rows[row] = mat.quantity
        elif await service.is_intermediate(mat.name):
            intermediates_rows[row] = mat.quantity
        elif await service.is_artifact_template(mat.name):
            artifact_templates_rows[row] = mat.quantity

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


async def txn(dto: TxnDTO, title: str) -> list[str]:
    rows = []

    if dto.empty():
        return [f'{title}\n\n<i>{glob.TXN_TRANS_HISTORY_EMPTY}</i>']

    for addt in dto.addts:
        row = (f"✨🔹 | id: {addt.ticket_txn_id}"
               f" | <b>+{addt.transfer / 100:.2f}</b>"
               f" | {funcs.to_kyiv_str(addt.time)}"
               f" | {glob.TXN_TEXT}: <i>{addt.description}</i>")
        rows.append((row, addt.time))

    for delt in dto.delts:
        row = (f"✨🔻 | id: {delt.ticket_txn_id}"
               f" | <b>-{delt.transfer / 100:.2f}</b>"
               f" | {funcs.to_kyiv_str(delt.time)}"
               f" | {glob.TXN_TEXT}: <i>{delt.description}</i>")
        rows.append((row, delt.time))

    for tpay, tax in dto.tpays.items():
        if tpay.receiver_id == dto.user_id:
            member = _find_member(dto.unique_transfer_members, tpay.sender_id)
            sender_name = get_formatted_name(member)

            row = (f"🔀🔹 | id: {tpay.ticket_txn_id}"
                   f" | {glob.TXN_FROM}: <b>{sender_name}</b>"
                   f" | <b>+{tpay.transfer / 100:.2f}</b>"
                   f" | {funcs.to_kyiv_str(tpay.time)}"
                   f" | {glob.TXN_TEXT}: <i>{tpay.description}</i>")
        else:
            member = _find_member(dto.unique_transfer_members, tpay.receiver_id)
            receiver_name = get_formatted_name(member)

            row = (f"🔀🔻 | id: {tpay.ticket_txn_id}"
                   f" | {glob.TXN_TO}: <b>{receiver_name}</b>"
                   f" | <b>-{tpay.transfer / 100:.2f}</b>"
                   f" | -{tax / 100:.2f}"
                   f" | {funcs.to_kyiv_str(tpay.time)}"
                   f" | {glob.TXN_TEXT}: <i>{tpay.description}</i>")

        rows.append((row, tpay.time))

    for msend, tax in dto.msends.items():
        if msend.receiver_id == dto.user_id:
            member = _find_member(dto.unique_transfer_members, msend.sender_id)
            sender_name = get_formatted_name(member)

            row = (f"〽️🔹 | id: {msend.ticket_txn_id}"
                   f" | {glob.TXN_FROM}: <b>{sender_name}</b>"
                   f" | <b>+{msend.transfer / 100:.2f}</b>"
                   f" | {funcs.to_kyiv_str(msend.time)}"
                   f" | {glob.TXN_TEXT}: <i>{msend.description}</i>")
        else:
            member = _find_member(dto.unique_transfer_members, msend.receiver_id)
            receiver_name = get_formatted_name(member)

            row = (f"〽️🔻 | id: {msend.ticket_txn_id}"
                   f" | {glob.TXN_TO}: <b>{receiver_name}</b>"
                   f" | <b>-{msend.transfer / 100:.2f}</b>"
                   f" | -{tax / 100:.2f}"
                   f" | {funcs.to_kyiv_str(msend.time)}"
                   f" | {glob.TXN_TEXT}: <i>{msend.description}</i>")

        rows.append((row, msend.time))

    for msell in dto.msells:
        row = (f"📦🔹 | id: {msell.ticket_txn_id}"
               f" | <b>+{msell.transfer / 100:.2f}</b>"
               f" | {funcs.to_kyiv_str(msell.time)}"
               f" | {glob.TXN_TEXT}: <i>{msell.description}</i>")
        rows.append((row, msell.time))

    for salary in dto.salaries:
        row = (f"💸🔹 | id: {salary.ticket_txn_id}"
               f" | <b>+{salary.transfer / 100:.2f}</b>"
               f" | {funcs.to_kyiv_str(salary.time)}"
               f" | {glob.TXN_TEXT}: <i>{salary.description}</i>")
        rows.append((row, salary.time))

    for award in dto.awards:
        row = (f"🎖🔹 | id: {award.ticket_txn_id}"
               f" | <b>+{award.transfer / 100:.2f}</b>"
               f" | {funcs.to_kyiv_str(award.time)}"
               f" | {glob.TXN_TEXT}: <i>{award.description}</i>")
        rows.append((row, award.time))

    for unknown in dto.unknowns:
        row = f"❔🔹 | id: {unknown.ticket_txn_id} | <b>+{unknown.transfer / 100:.2f}</b>" \
            if unknown.transfer > 0 else \
            f"❔🔻 | id: {unknown.ticket_txn_id} | <b>-{unknown.transfer / 100:.2f}</b>"
        row += f" | {funcs.to_kyiv_str(unknown.time)} | {glob.TXN_TEXT}: <i>{unknown.description}</i>"
        rows.append((row, unknown.time))

    for tax in dto.taxes:
        row = (f"🧾🔻 | id: {tax.tax_txn_id}"
               f" | tax type: <b>{tax.tax_type}</b>"
               f" | <b>-{tax.amount / 100:.2f}</b>"
               f" | txn-id: {tax.parent_id} (table: <i>{tax.parent_type}</i>)"
               f" | {funcs.to_kyiv_str(tax.time)}")
        rows.append((row, tax.time))

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
                      f"\n{glob.PAGE_GEN_PAYMENT}: <b>{ar.award.payment / 100:.2f} tc</b>"
                      f"\n{glob.PAGE_GEN_ISSUED}: <b>{funcs.to_kyiv_str(ar.issue_date)}</b>"
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
