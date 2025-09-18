import copy
import random
from datetime import datetime, timedelta, timezone
from sqlite3 import IntegrityError
from typing import Optional, List, Any

import aiofiles
import yaml
from aiogram.types import User, Message

import resources.glob as glob
from command.parser.results import CommandParserResult
from command.parser.types import CommandTargetType as CTT
from model.database.awards import Award, AwardMember
from model.database.materials import Recipe, Material, Ingredient, MemberMaterial, Artifact, MaterialOrder, MaterialDeal
from model.database.member import Member, DelMember
from model.database.transactions import TicketTransaction, BusinessProfitTransaction, MaterialTransaction, \
    TaxTransaction
from model.dto.award_dto import AwardDTO
from model.dto.ltrans_dto import TxnDTO
from model.dto.msend_dto import MaterialOrderCostDetailsDTO
from model.dto.txn_dto import TransactionResultDTO
from model.types.custom.primitives import OrderCode
from model.types.enums import TicketTxnType, ProfitType, MaterialTxnType, TransactionResultErrors as TRE, TaxType, \
    TaxParentType, OrderingType, GemCountingMode, ArtifactType, MaterialDealStatus, MaterialDealResult
from repository import repository_core as repo
from utils import funcs
from service.operational.manager import ServiceOperationsManager
from utils.funcs import get_formatted_name, get_single_tax, utcnow_str, get_materials_yaml

_som: Optional[ServiceOperationsManager] = None
sfs_alert_pins: dict[int, Message] = {}

_recipes: list[Recipe] = []
_materials: list[Material] = []
_gem_freq: dict[str, float] = {}
_artifact_profit: dict[str, float] = {}

""" Glob Getters """


def som() -> ServiceOperationsManager:
    global _som
    if not _som:
        _som = ServiceOperationsManager()
    return _som


async def _get_recipes() -> List[Recipe]:
    global _recipes

    if not _recipes:
        async with aiofiles.open(glob.RECIPES_YAML_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(await f.read())

        _recipes = [
            Recipe(
                result=Ingredient(**item['result']),
                ingredients=[Ingredient(**ingr) for ingr in item['ingredients']]
            ) for item in data
        ]

    return _recipes


async def _get_materials() -> list[Material]:
    global _materials
    if not _materials:
        _materials = await get_materials_yaml()
    return _materials


async def _get_gem_freq() -> dict[str, float]:
    global _gem_freq
    if not _gem_freq:
        async with aiofiles.open(glob.GEM_FREQ_YAML_PATH, 'r', encoding='utf-8') as f:
            _gem_freq = yaml.safe_load(await f.read())
    return _gem_freq


async def _get_artifact_profits_dict() -> dict[str, float]:
    global _artifact_profit
    if not _artifact_profit:
        async with aiofiles.open(glob.ARTIFACT_PROFIT_YAML_PATH, 'r', encoding='utf-8') as f:
            _artifact_profit = yaml.safe_load(await f.read())
    return _artifact_profit


""" General """


async def sql_execute(query: str, many: bool = False) -> (bool, str):
    return await repo.sql_execute(query, many)


async def _transfer_tickets(
        *, sender: Member, receiver: Member, amount: int,
        txn_type: TicketTxnType, description: str = None, created_at: str = None
) -> int:
    """
    Use only for TicketTransaction transfers
    :param created_at: ISO-8601 String (the combined date and time in UTC format)
    :return: Ticket Transaction ID (ticket_txns)
    """
    sender.tickets -= amount
    receiver.tickets += amount

    await repo.update_member_tickets(sender)
    await repo.update_member_tickets(receiver)

    return await repo.insert_ticket_txn(TicketTransaction(
        sender_id=sender.user_id,
        receiver_id=receiver.user_id,
        transfer=amount,
        txn_type=txn_type,
        time=created_at if created_at else utcnow_str(),
        description=description
    ))


async def _add_tickets(member: Member, amount: int, txn_type: TicketTxnType, description: str = None):
    """
    :return: ticket transaction id
    """
    member.tickets += amount
    created_at = utcnow_str()

    await repo.update_member_tickets(member)
    return await repo.insert_ticket_txn(TicketTransaction(
        receiver_id=member.user_id,
        transfer=amount,
        time=created_at,
        description=description,
        txn_type=txn_type
    ))


async def _del_tickets(member: Member, tickets: int, txn_type: TicketTxnType, description: str = None):
    """
    :return: ticket transaction id
    """
    member.tickets -= tickets
    created_at = utcnow_str()

    await repo.update_member_tickets(member)
    await repo.insert_ticket_txn(TicketTransaction(
        sender_id=member.user_id,
        transfer=tickets,
        time=created_at,
        description=description,
        txn_type=txn_type
    ))


async def _set_tickets(member: Member, amount: int, txn_type: TicketTxnType, description: str = None) -> int:
    """
    :return: ticket transaction id
    """
    if member.tickets == amount:
        return 0

    created_at = utcnow_str()

    if amount > member.tickets:  # addt
        transfer = amount - member.tickets
        await repo.insert_ticket_txn(TicketTransaction(
            receiver_id=member.user_id,
            transfer=transfer,
            txn_type=txn_type,
            time=created_at,
            description=description
        ))
    else:  # delt
        transfer = member.tickets - amount
        await repo.insert_ticket_txn(TicketTransaction(
            sender_id=member.user_id,
            transfer=transfer,
            txn_type=txn_type,
            time=created_at,
            description=description
        ))

    init_member_tickets = member.tickets
    member.tickets = amount
    await repo.update_member_tickets(member)

    return transfer if amount > init_member_tickets else -transfer


async def _profit_business_account(member: Member, transfer: int, profit_type: ProfitType, artifact_id: int):
    member.business_account += transfer
    date = utcnow_str()

    await repo.update_member_business_account(member)
    await repo.insert_business_profit(BusinessProfitTransaction(
        user_id=member.user_id,
        profit_type=profit_type,
        transfer=transfer,
        date=date,
        artifact_id=artifact_id
    ))


""" Public Interfaces """


async def infm(m: Member) -> str:
    jobs = str()
    for pn in await get_job_names(m.user_id):
        jobs += f'\n~ {pn}'

    return (f"{glob.INFM_TEXT}"
            f"\n\n<b>{glob.INFM_PERSONAL_INFO}</b>"
            f"\nid: {m.user_id}"
            f"\n{glob.INFM_FIRST_NAME}: {'-' if m.first_name is None else m.first_name}"
            f"\n{glob.INFM_LAST_NAME}: {'-' if m.last_name is None else m.last_name}"
            f"\n{glob.INFM_USERNAME}: {'-' if m.username is None else m.username}"
            f"\n\n<b>{glob.INFM_JOBS}</b>"
            f"{jobs}"
            f"\n\n<b>{glob.INFM_COLLECTION}</b>"
            f"\n{glob.INFM_ARTIFACTS}: {await repo.get_artifacts_count(m.user_id)}"
            f"\n{glob.INFM_AWARDS}: {await repo.get_awards_count(m.user_id)}"
            f"\n\n<b>{glob.INFM_ASSETS}</b>"
            f"\n{glob.INFM_PERSONAL}: {'+' if m.tickets > 0 else str()}{m.tickets / 100:.2f}"
            f"\n{glob.INFM_BUSINESS}: {'+' if m.business_account > 0 else str()}{m.business_account / 100:.2f}"
            f"\n{glob.INFM_TRANS_AVAILABLE}: {m.tpay_available}"
            f"\n{glob.INFM_TBOX_AVAILABLE}: {m.tbox_available}")


async def bal(m: Member) -> str:
    name = get_formatted_name(member=m, ping=True)
    sign = '+' if m.tickets > 0 else str()
    return (f"{glob.BAL_NAME}: {name}"
            f"\n{glob.BAL_PERSONAL}: {sign}{m.tickets / 100:.2f}"
            f"\n{glob.BAL_BUSINESS}: {sign}{m.business_account / 100:.2f}"
            f"\n{glob.BAL_TPAY_AVAILABLE}: {m.tpay_available}"
            f"\n{glob.BAL_TBOX_AVAILABLE}: {m.tbox_available}")


async def balm(user_id: int) -> tuple[int, list[Ingredient]]:
    materials: list[Ingredient] = await repo.get_member_materials_by_user_id(user_id)
    return user_id, materials


async def tbox(user_id: int) -> str:
    member = await get_member(user_id)

    if member.tbox_available == 0:
        return glob.TBOX_UNAVAILABLE_ERROR

    gems = await _get_rand_gemstones()
    await repo.spend_tbox_available(member.user_id)
    await repo.add_member_material(user_id, gems)
    await repo.insert_material_transaction(MaterialTransaction(
        receiver_id=user_id,
        type_=MaterialTxnType.TBOX,
        material_name=gems.name,
        quantity=gems.quantity,
        date=utcnow_str()
    ))

    return (f"*{glob.TBOX_OPENED_TEXT}*\n"
            f"{glob.TBOX_MEMBER}: {get_formatted_name(member)}\n\n"
            f"+{gems.quantity}{await get_emoji(gems.name)} ({gems.name})")


async def tpay(sender: Member, receiver: Member, transfer: int, description: str = None) -> TransactionResultDTO:
    single_tax = await get_single_tax(transfer)

    if transfer + single_tax > sender.tickets:
        return TransactionResultDTO(TRE.INSUFFICIENT_FUNDS)

    created_at = utcnow_str()

    # transfer & tpay available
    await repo.spend_tpay_available(sender.user_id)
    ticket_txn_id = await _transfer_tickets(
        sender=sender,
        receiver=receiver,
        amount=transfer,
        txn_type=TicketTxnType.TPAY,
        description=description,
        created_at=created_at
    )

    # taxation
    sender.tickets -= single_tax
    await repo.update_member_tickets(sender)
    await repo.insert_tax_txn(TaxTransaction(
        parent_id=ticket_txn_id,
        user_id=sender.user_id,
        amount=single_tax,
        tax_type=TaxType.SINGLE,
        parent_type=TaxParentType.TICKET,
        time=created_at
    ))

    return TransactionResultDTO(valid=True)


async def msell(data: dict[str, Any]):
    user_id: int = data['user_id']
    material: Material = data['material']
    quantity: int = data['quantity']
    revenue: int = data['revenue']
    single_tax: int = data['single_tax']
    msell_tax: int = data['msell_tax']
    member = await get_member(user_id)
    current_datetime = utcnow_str()

    # tickets transaction
    member.tickets += revenue
    await repo.update_member_tickets(member)
    ticket_txn_id = await repo.insert_ticket_txn(TicketTransaction(
        receiver_id=user_id,
        transfer=revenue,
        txn_type=TicketTxnType.MSELL,
        time=current_datetime,
        description=f'{TicketTxnType.MSELL.value} - {quantity} ({material.name})'
    ))

    # single taxation
    member.tickets -= single_tax
    await repo.update_member_tickets(member)
    await repo.insert_tax_txn(TaxTransaction(
        parent_id=ticket_txn_id,
        user_id=user_id,
        amount=single_tax,
        tax_type=TaxType.SINGLE,
        parent_type=TaxParentType.TICKET,
        time=current_datetime,
    ))

    # msell taxation
    member.tickets -= msell_tax
    await repo.update_member_tickets(member)
    await repo.insert_tax_txn(TaxTransaction(
        parent_id=ticket_txn_id,
        user_id=user_id,
        amount=msell_tax,
        tax_type=TaxType.MSELL,
        parent_type=TaxParentType.TICKET,
        time=current_datetime,
    ))

    # materials transaction
    diff = Ingredient(material.name, quantity)
    await repo.spend_tpay_available(user_id)
    await repo.spend_member_material(user_id, diff)
    await repo.insert_material_transaction(MaterialTransaction(
        sender_id=user_id,
        type_=MaterialTxnType.MSELL,
        material_name=material.name,
        quantity=quantity,
        ticket_txn=ticket_txn_id,
        date=current_datetime
    ))


async def txn(user_id: int) -> TxnDTO:
    return await repo.get_txn_stats(user_id)


async def laward(user_id: int) -> Optional[List[AwardDTO]]:
    return await repo.get_awards(user_id)


async def topt(size: int = 0, percent_flag: bool = False, id_flag: bool = False) -> str:
    if size:
        order = OrderingType.DESC if size > 0 else OrderingType.ASC
        limit = abs(size)
        header = glob.TOPT_DESC if order == OrderingType.DESC else glob.TOPT_ASC
    else:
        order = OrderingType.DESC
        limit = None
        header = f'{glob.TOPT_DESC} {glob.TOP_FULL}'

    total_tickets = await repo.get_sum_tickets()
    tpool_ = await get_tpool()
    members = await repo.get_topt_members(order, limit)

    lines = [
        header,
        f'{glob.TOPT_TICKETS_TOTAL}: {total_tickets / 100:.2f} tc',
        f'{glob.TOPT_TPOOL}: {tpool_ / 100:.2f} tc',
        ''
    ]

    medals = {1: '🥇', 2: '🥈', 3: '🥉'}
    for idx, m in enumerate(members, start=1):
        if idx <= 3 and (limit is None or order == OrderingType.DESC):
            iterator = medals[idx]
        else:
            iterator = f'{idx}.'

        if percent_flag:
            if total_tickets > 0:
                pct = m.tickets / total_tickets * 100
                value = f'{pct:.2f}%'
            else:
                value = glob.TOP_BANKRUPT
        else:
            sign = '+' if m.tickets > 0 else ''
            value = f'{sign}{m.tickets / 100:.2f}'

        uid_str = f'`{m.user_id}` ' if id_flag else ''
        name = get_formatted_name(m)[:32]
        lines.append(f'{iterator} {uid_str}({value}) {name}')

        if idx == 3:
            lines.append('')

    return '\n'.join(lines)


async def topm(size: int = 0, percent_mode: bool = False, id_mode: bool = False) -> str:
    member_materials: list[MemberMaterial] = await repo.get_all_member_materials()
    gem_rates: dict[str, float] = await repo.get_gem_rates_dict()
    member_accounts: dict[int, float] = {}  # (!) taxed values

    for mm in member_materials:
        member_accounts.setdefault(mm.user_id, 0)
        base = mm.quantity * (1 - glob.SINGLE_TAX)
        mat_rank = await get_material_rank(mm.material_name)

        if mat_rank == 1:
            member_accounts[mm.user_id] += base * gem_rates[mm.material_name]
        else:
            mat_price = await get_gc_value(
                await get_gc_by_recipe(
                    await _find_recipe(mm.material_name)
                )
            )
            member_accounts[mm.user_id] += base * mat_price * (glob.MAT_RANK_UPVAL ** (mat_rank - 1))

    if size:
        order = OrderingType.DESC if size > 0 else OrderingType.ASC
        limit = abs(size)
        header = glob.TOPM_DESC if order == OrderingType.DESC else glob.TOPM_ASC
    else:
        order = OrderingType.DESC
        limit: Optional[int] = None
        header = f'{glob.TOPM_DESC} {glob.TOP_FULL}'

    total = sum(member_accounts.values())
    taxed_mpool = await get_material_tpool()
    pure_mpool = taxed_mpool / (1 - glob.SINGLE_TAX)

    items = sorted(
        member_accounts.items(),
        key=lambda kv: kv[1],
        reverse=(order == OrderingType.DESC)
    )

    if limit is not None:
        items = items[:limit]

    lines = [
        header,
        f'{glob.TOPM_PURE_MPOOL}: {pure_mpool / 100:.2f} tc',
        f'{glob.TOPM_TAXED_MPOOL}: {taxed_mpool / 100:.2f} tc',
        f'\n_{glob.TOPM_PURE_DISCLAIMER}_',
        ''
    ]

    medals = {1: '🥇', 2: '🥈', 3: '🥉'}
    for idx, (uid, val) in enumerate(items, start=1):
        if idx <= 3 and (limit is None or order == OrderingType.DESC):
            iterator = medals[idx]
        else:
            iterator = f'{idx}.'

        if percent_mode:
            value = f'{val / total * 100:.2f}%' if total > 0 else glob.TOP_BANKRUPT
        else:
            value = f'{val / 100:.2f}'

        uid_str = f'[{uid}] ' if id_mode else ''
        member = await get_member(uid)
        name = get_formatted_name(member)[:32]
        lines.append(f'{iterator} {uid_str}({value}) {name}')

        if idx == 3:
            lines.append('')

    return '\n'.join(lines)


async def tpool() -> str:
    personal_tpool = await get_total_tickets()
    business_tpool = await get_business_tpool()
    # artifact_tpool = await get_artifact_tpool()
    material_tpool = await get_material_tpool()

    nbt_tpool = await get_nbt_tpool()
    total_tpool = await get_tpool()

    return (f'{glob.TPOOL_PERSONAL}: {personal_tpool / 100:.2f} tc'
            f'\n{glob.TPOOL_BUSINESS}: {business_tpool / 100:.2f} tc'
            # f'\n{glob.TPOOL_ARTIFACT}: {artifact_tpool / 100:.2f} tc'
            f'\n{glob.TPOOL_MATERIAL}: {material_tpool / 100:.2f} tc'
            f'\n\n{glob.TPOOL_NBT}: {nbt_tpool / 100:.2f} tc'
            f'\n*{glob.TPOOL_TOTAL}: {total_tpool / 100:.2f} tc*')


async def rates() -> str:
    rh = await repo.get_last_rate_history()

    gem_rates_view = str()
    for name, rate in (await repo.get_gem_rates_dict()).items():
        gem_rates_view += f'\n{await get_emoji(name)}*{name}*: {rate / 100:.7f} tc'

    return (f'*\n{glob.RATES_REAL_INFL}: {(rh.inflation * rh.fluctuation - 1) * 100:.2f}%*'
            f'\n\n{glob.RATES_PURE_INFL}: {(rh.inflation - 1) * 100:.2f}%'
            f'\n{glob.RATES_FLUCT}: {(rh.fluctuation - 1) * 100:.2f}%'
            f'\n{gem_rates_view}')


async def p(price: float) -> str:
    adjusted_price, inflation, fluctuation = await _get_infl_rate_adjustments(price)
    return (f'{glob.P_BASE_PRICE}:\n{price / 100:.2f} tc\n'
            f'\n{glob.P_ADJUSTED_PRICE}: {adjusted_price / 100:.2f} tc'
            f'\n{glob.P_INFLATION}: {(inflation - 1) * 100:.2f}%'
            f'\n{glob.P_FLUCTUATION}: {(fluctuation - 1) * 100:.3f}%')


async def anchor(user_id: int, chat_id: int) -> str:
    member = await get_member(user_id)

    if member.anchor == chat_id:
        return glob.ANCHOR_REJECTED

    member.anchor = chat_id
    await repo.update_member_anchor(member)
    return glob.ANCHOR_SUCCESS


""" Admin Interfaces """


async def addt(member: Member, tickets: int, description: str = None):
    await _add_tickets(member, tickets, TicketTxnType.ADMIN, description)


async def delt(member: Member, tickets: int, description: str = None):
    await _del_tickets(member, tickets, TicketTxnType.ADMIN, description)


async def sett(member: Member, tickets: int, description: str = None) -> int:
    return await _set_tickets(member, tickets, TicketTxnType.ADMIN, description)


async def award(m: Member, a: Award, issue_date: str):
    if a.payment > 0:
        await pay_award(
            member=m,
            payment=a.payment,
            description=a.award_id
        )

    payment = f'\n{glob.AWARD_PAYMENT}: <b>{a.payment / 100:.2f} tc</b>' \
        if a.payment > 0 else str()

    return (f"{glob.AWARD_SUCCESS}"
            f"\n\n<b>{a.name}</b>"
            f"\n\nid: <b>{a.award_id}</b>"
            f"{payment}"
            f"\n{glob.AWARD_ISSUED}: <b>{funcs.to_kyiv_str(issue_date)}</b>"
            f"\n\n<b>{glob.AWARD_STORY}</b>: <i>{a.description}</i>")


async def hire(member: Member, position: str) -> str:
    await repo.insert_employee(
        user_id=member.user_id,
        position=position,
        hired_date=utcnow_str()
    )

    positions = f'{glob.HIRE_JOBS} {get_formatted_name(member)}:'
    for pn in await get_job_names(member.user_id):
        positions += f'\n~ {pn}'

    return f'{glob.MEMBER_HIRED}\n\n{positions}'


async def fire(user_id: int, position: str) -> bool:
    employee = await repo.get_employee(user_id, position)

    if employee is None:
        return False
    else:
        await repo.insert_employment_history(employee, utcnow_str())
        await repo.delete_employee(user_id, position)
        return True


async def unreg(member: Member, otype: str):
    await _set_tickets(
        member=member,
        amount=0,
        txn_type=TicketTxnType.UNREG,
        description='unreg'
    )

    if otype == glob.BAN_FLAG:
        await repo.insert_del_member(DelMember(
            user_id=member.user_id,
            username=member.username,
            first_name=member.first_name,
            last_name=member.last_name,
            anchor=member.anchor
        ))

    await repo.delete_member(member.user_id)


""" Get """


async def get_member(user_id: int) -> Optional[Member]:
    return await repo.get_member_by_user_id(user_id)


async def get_del_member(user_id: int) -> Optional[DelMember]:
    return await repo.get_del_member_by_user_id(user_id)


async def get_target_member(cpr: CommandParserResult) -> Optional[Member]:
    if cpr.overload.target_type == CTT.NONE:
        user_id = cpr.message.from_user.id
        return await repo.get_member_by_user_id(user_id)
    elif cpr.overload.target_type == CTT.REPLY:
        user_id = cpr.message.reply_to_message.from_user.id
        return await repo.get_member_by_user_id(user_id)
    elif cpr.overload.target_type == CTT.USERNAME:
        return await repo.get_member_by_username(cpr.args[glob.USERNAME_ARG])
    elif cpr.overload.target_type == CTT.USER_ID:
        return await repo.get_member_by_user_id(cpr.args[glob.USER_ID_ARG])


async def get_award(cpr: CommandParserResult) -> Optional[Award]:
    return await repo.get_award(cpr.args[glob.AWARD_ID_ARG])


async def get_job_names(user_id: int) -> Optional[List[str]]:
    return await repo.get_job_names(user_id)


async def get_job_name(position: str) -> Optional[str]:
    return await repo.get_job_name(position)


async def get_tpool(infl: bool = False) -> float:
    return sum([
        await get_total_tickets(),
        await get_business_tpool(),
        # await get_artifact_tpool(),
        await get_material_tpool(infl)
    ])


async def get_nbt_tpool() -> int:
    return await repo.get_nbt()


async def get_total_tickets() -> int:
    return await repo.get_sum_tickets()


async def get_business_tpool() -> int:
    return await repo.get_sum_business_accounts()


async def get_material_tpool(infl: bool = False, taxed: bool = True) -> float:
    pure_mpool = await get_gc_value(
        await get_mpool_gc(GemCountingMode.PRICING)
    )

    taxed_mpool = pure_mpool * (1 - glob.SINGLE_TAX)

    if not infl:
        return taxed_mpool if taxed else pure_mpool

    month_sold = await repo.get_sold_mat_revenue_by_period(
        start_day=datetime.now(timezone.utc) - timedelta(days=30)
    )

    return month_sold / 30

    # artifact_mtpool = sum([
    #     await get_artifact_creation_price(a)
    #     for a in await repo.get_all_artifacts()
    # ])

    # return round(artifact_mtpool + (1 - glob.SINGLE_TAX) * raw_mtpool, 2)


async def get_artifact_price(a: Artifact) -> float:
    return a.age_multiplier() * a.investment + await get_artifact_creation_price(a)


async def get_artifact_creation_price(a: Artifact) -> float:
    return await get_gc_value(
        await get_gc_by_recipe(
            await _find_recipe(
                f'{a.type_}_artifact'
            )))


async def get_material_rank(material_name: str) -> int:
    rank = 2

    r = await _find_recipe(material_name)
    if r is None:
        return 1

    for ingr in r.ingredients:
        if not any(ingr.name == m.name for m in await get_gems_list()):
            rank = max(rank, 1 + await get_material_rank(ingr.name))

    return rank


async def get_gems_list() -> list[Material]:
    return (await _get_materials())[:7]


async def get_intermediates_list() -> list[Material]:
    return (await _get_materials())[7:-5]


async def get_artifact_templates_list() -> list[Material]:
    return (await _get_materials())[-5:]


async def get_gc_value(gem_counts: dict[str, float]) -> float:
    gem_rates = await repo.get_gem_rates_dict()
    return sum(
        count * gem_rates[name]
        for name, count in gem_counts.items()
    )


async def get_gc_by_recipe(r: Recipe) -> dict[str, float]:
    gem_counts = {g.name: 0. for g in await get_gems_list()}
    all_inner_gc = []

    for ingr in r.ingredients:
        norm = ingr.quantity / r.result.quantity
        if ingr.name in gem_counts:
            gem_counts[ingr.name] = norm
        else:
            inner_gc = await get_gc_by_recipe(
                await _find_recipe(ingr.name)
            )
            for key, value in inner_gc.items():
                inner_gc[key] = value * norm
            all_inner_gc.append(inner_gc)

    if all_inner_gc:
        result = {g.name: 0. for g in await get_gems_list()}
        all_gc = [gem_counts, *all_inner_gc]
        for pc in all_gc:
            for key, value in pc.items():
                result[key] += value
        return result
    else:
        return gem_counts


async def get_gc_by_list(ingredients: list[Ingredient], mode: GemCountingMode) -> dict[str, float]:
    mpool_gem_counts = {g.name: 0. for g in await get_gems_list()}
    rank_gradation = glob.MAT_RANK_UPVAL if mode == GemCountingMode.PRICING else glob.MAT_RANK_DEVAL

    for mat in ingredients:
        mat_rank = await get_material_rank(mat.name)
        if mat_rank == 1:
            mpool_gem_counts[mat.name] += mat.quantity
        else:
            r = await _find_recipe(mat.name)
            for g_name, g_count in (await get_gc_by_recipe(r)).items():
                mpool_gem_counts[g_name] += mat.quantity * g_count * (rank_gradation ** (mat_rank - 1))

    return mpool_gem_counts


async def get_mpool_gc(mode: GemCountingMode) -> dict[str, float]:
    return await get_gc_by_list(
        await repo.get_each_material_count(),
        mode
    )


async def get_emoji(material_name: str) -> Optional[str]:
    for m in await _get_materials():
        if m.name == material_name:
            return m.emoji


async def get_material_name(emoji: str) -> Optional[str]:
    for m in await _get_materials():
        if m.emoji == emoji:
            return m.name


async def get_member_material(user_id: int, material_name: str) -> Optional[Ingredient]:
    return await repo.get_member_material(user_id, material_name)


async def get_sold_mc_today(user_id: int) -> int:
    # default: the period of one day (yesterday)
    return await repo.get_member_sold_mc_by_period(user_id)


async def get_material_price(material_name: str) -> float:
    return await repo.get_material_price(material_name)


async def get_formatted_material_name(material_name: str) -> Optional[str]:
    if material_name:
        return material_name.replace('_', ' ')


async def get_materials_markup(user_id: int) -> list[list[str]]:
    materials = await repo.get_member_materials_by_user_id(user_id)
    reservations = await repo.get_material_reservations(user_id)

    # dict[str, int]
    gemstone_buttons = {}
    intermediates_buttons = {}
    artifact_templates_buttons = {}

    for ing in materials:
        reserved = reservations.get(ing.name, 0)
        reserved_str = f' (-{reserved})' if reserved > 0 else ''
        btn = f'{await get_emoji(ing.name)} {ing.quantity}{reserved_str}\n'

        if await is_gem(ing.name):
            gemstone_buttons[btn] = ing.quantity
        elif await is_intermediate(ing.name):
            intermediates_buttons[btn] = ing.quantity
        elif await is_artifact_template(ing.name):
            artifact_templates_buttons[btn] = ing.quantity

    def _form_button_groups(rows: dict[str, int]) -> list[str]:
        return sorted(rows, key=rows.get, reverse=True)

    gemstones_group = _form_button_groups(gemstone_buttons)
    intermediates_group = _form_button_groups(intermediates_buttons)
    artifact_templates_group = _form_button_groups(artifact_templates_buttons)

    def _split_into_rows(button_group: list[str]) -> list[list[str]]:
        btn_count = int(len(button_group) / glob.CHOOSE_MAT_BTN_ROW_LIMIT) + 1
        rows = list()
        for i in range(0, btn_count):
            beg = glob.CHOOSE_MAT_BTN_ROW_LIMIT * i
            end = glob.CHOOSE_MAT_BTN_ROW_LIMIT * (i + 1)
            rows.append(button_group[beg:end])
        return rows

    return list(filter(bool, [
        *_split_into_rows(gemstones_group),
        *_split_into_rows(intermediates_group),
        *_split_into_rows(artifact_templates_group)
    ]))


async def get_material_reservation(sender_id: int, material_name: str) -> int:
    return await repo.get_material_reservation(sender_id, material_name)


async def get_material_reservations(sender_id: int) -> dict[str, int]:
    return await repo.get_material_reservations(sender_id)


""" Member """


async def reg_member(sender: User, target: User, anchor_: int) -> bool:
    dm = await get_del_member(target.id)
    is_creator = glob.rms.is_admin(sender.id)

    if dm is not None:
        if not is_creator:
            return False
        await repo.delete_del_member(target.id)

    await repo.insert_member(Member(
        user_id=target.id,
        username=target.username,
        first_name=target.first_name,
        last_name=target.last_name,
        anchor=anchor_
    ))

    return True


async def update_member(user: User, member: Member = None):
    if member is None:
        member = await repo.get_member_by_user_id(user.id)

    updated_member = copy.deepcopy(member)
    changed = False

    if member.username != user.username:
        changed = True
        updated_member.username = user.username

    if member.first_name != user.first_name:
        changed = True
        updated_member.first_name = user.first_name

    if member.last_name != user.last_name:
        changed = True
        updated_member.last_name = user.last_name

    if changed:
        await repo.update_member_names(updated_member)


""" Award """


async def issue_award(am: AwardMember) -> bool:
    return await repo.insert_award_member(am)


async def pay_award(member: Member, payment: int, description: str):
    await _add_tickets(member, payment, TicketTxnType.AWARD, description)


""" Msend """


async def msend_reserve(data: dict[str, Any]) -> Optional[MaterialOrder]:
    """
    :param data: FSMContext's get_data()
    :return: (True, invoice_code) || (False, error_message)
    """
    mat_sender_id: int = data['mat_sender_id']
    mat_receiver_id: int = data['mat_receiver_id']
    quantity: int = data['quantity']
    offered_cost: int = data['offered_cost']
    description: str = data['description']
    material_name: str = data['material_name']

    material_bal: Ingredient = await get_member_material(
        user_id=mat_sender_id,
        material_name=material_name
    )

    if material_bal is None or material_bal.quantity < quantity:
        return None

    order = MaterialOrder(
        code=OrderCode.generate_random(),
        sender_id=mat_sender_id,
        receiver_id=mat_receiver_id,
        material_name=material_name,
        quantity=quantity,
        offered_cost=offered_cost,
        created_at=funcs.utcnow_str(),
        description=description
    )

    while True:
        try:  # seeking for a free primary key
            await repo.insert_material_order(order)
            break
        except IntegrityError:
            order.code = OrderCode.generate_random()

    return order


async def accept_trade_deal(order: MaterialOrder) -> MaterialDealResult:
    # error capturing
    if not order:
        return MaterialDealResult.ORDER_NOT_FOUND

    sender = await get_member(order.sender_id)
    if not sender:
        return MaterialDealResult.SENDER_NOT_FOUND

    receiver = await get_member(order.receiver_id)
    if not receiver:
        return MaterialDealResult.RECEIVER_NOT_FOUND

    material_bal: Ingredient = await get_member_material(sender.user_id, order.material_name)
    if not material_bal:
        return MaterialDealResult.MATERIAL_NOT_FOUND

    reserved: int = await repo.get_material_reservation_exclude_receiver(
        sender_id=sender.user_id,
        receiver_id=receiver.user_id,
        material_name=order.material_name
    )

    available = material_bal.quantity - reserved
    if order.quantity > material_bal.quantity:
        return MaterialDealResult.NOT_ENOUGH_MATERIAL
    if order.quantity > available:
        return MaterialDealResult.RESERVATION_VIOLATED

    # transfer materials
    material_transfer = Ingredient(name=order.material_name, quantity=order.quantity)
    await repo.spend_member_material(user_id=sender.user_id, diff=material_transfer)
    await repo.add_member_material(user_id=receiver.user_id, diff=material_transfer)

    # cost revaluation
    details = await calculate_material_order_cost_details(order.material_name, order.quantity, order.offered_cost)
    created_at = utcnow_str()

    # transfer tickets
    ticket_txn_id = await _transfer_tickets(
        sender=receiver,  # ticket sender = material receiver
        receiver=sender,  # ticket receiver = material sender
        amount=details.total_cost,
        txn_type=TicketTxnType.MSEND,
        description=order.description,
        created_at=created_at
    )

    # sender pays single tax
    sender.tickets -= details.single_tax
    await repo.update_member_tickets(sender)
    await repo.insert_tax_txn(TaxTransaction(
        parent_id=ticket_txn_id,
        user_id=sender.user_id,
        amount=details.single_tax,
        tax_type=TaxType.SINGLE,
        parent_type=TaxParentType.TICKET,
        time=created_at,
    ))

    # sender pays msend tax
    sender.tickets -= details.msend_tax
    await repo.update_member_tickets(sender)
    await repo.insert_tax_txn(TaxTransaction(
        parent_id=ticket_txn_id,
        user_id=sender.user_id,
        amount=details.msend_tax,
        tax_type=TaxType.MSEND,
        parent_type=TaxParentType.TICKET,
        time=created_at,
    ))

    # log material transaction
    mat_txn_id = await repo.insert_material_transaction(MaterialTransaction(
        sender_id=sender.user_id,
        receiver_id=receiver.user_id,
        type_=MaterialTxnType.MSEND,
        material_name=order.material_name,
        quantity=order.quantity,
        ticket_txn=ticket_txn_id,
        date=created_at,
        description=order.description
    ))

    # log material deal
    await repo.insert_material_deal(MaterialDeal(
        order_code=order.code,
        mat_txn_id=mat_txn_id,
        status=MaterialDealStatus.ACCEPTED,
        material_name=order.material_name,
        quantity=order.quantity,
        offered_cost=order.offered_cost,
        closed_at=created_at,
        order_created_at=funcs.to_iso_z(order.created_at),
        description=order.description
    ))

    # delete material order
    await repo.delete_material_order(order.code)

    # final
    return MaterialDealResult.SUCCESS


async def cancel_material_deal(order_code: str, status: MaterialDealStatus):
    if status not in [MaterialDealStatus.REJECTED, MaterialDealStatus.ABORTED]:
        raise ValueError('Invalid MaterialDealStatus at cancel_trade_deal')

    order: MaterialOrder = await get_material_order(order_code)
    if not order:
        return

    await repo.delete_material_order(order_code)
    await repo.insert_material_deal(MaterialDeal(
        order_code=order_code,
        status=status,
        material_name=order.material_name,
        quantity=order.quantity,
        offered_cost=order.offered_cost,
        closed_at=utcnow_str(),
        order_created_at=funcs.to_iso_z(order.created_at),
        description=order.description
    ))


""" Moffer """


async def get_moffer_details(order: MaterialOrder) -> Optional[str]:
    details = await calculate_material_order_cost_details(order.material_name, order.quantity, order.offered_cost)
    return (f'*{glob.MOFFER_MAT_ORDER}* `#{order.code}`\n_{glob.MOFFER_OFFER}_'
            f'\n\n{glob.MOFFER_SENDER}: {get_formatted_name(await get_member(order.sender_id), ping=True)}'
            f'\n{glob.MOFFER_RECEIVER}: {get_formatted_name(await get_member(order.receiver_id), ping=True)}'
            f'\n\n{glob.MOFFER_YOU_PAY}: *{details.total_cost / 100:.2f} tc*'
            f'\n{glob.MOFFER_YOU_RECEIVE}: *{order.quantity} {order.material_name}{await get_emoji(order.material_name)}*'
            f'\n\n{glob.MOFFER_OFFERED_TO_PAY}: {order.offered_cost / 100:.2f} tc'
            f'\n{glob.MOFFER_SINGLE_TAX_TEXT}: {details.single_tax / 100:.2f} tc ({int(glob.SINGLE_TAX * 100)}%)'
            f'\n{glob.MOFFER_MSEND_TAX_TEXT}: {details.msend_tax / 100:.2f} tc ({int(glob.MSEND_TAX * 100)}%)'
            f'\n\n{glob.MOFFER_RATE_PRICE}: {details.rate_price / 100:.7f} tc'
            f'\n{glob.MOFFER_OFFERED_PRICE}: {details.offered_price / 100:.7f} tc'
            f'\n\n{glob.MOFFER_DESCRIPTION}: _{order.description}_')


async def get_moffers_page(user_id: int) -> Optional[str]:
    orders: list[MaterialOrder] = await repo.get_receiver_material_orders(user_id)
    if not orders or len(orders) == 0:
        return f'_{glob.MOFFER_EMPTY}_'

    moffer_list = []
    for order in orders:
        sender = await get_member(order.sender_id)
        details = await calculate_material_order_cost_details(order.material_name, order.quantity, order.offered_cost)
        moffer_list.append(
            f'`#{order.code}`'
            f' | {glob.MOFFER_FROM}: {get_formatted_name(sender, ping=True)}'
            f' | *{order.quantity} {order.material_name}{await get_emoji(order.material_name)}*'
            f' | {glob.MOFFER_COST}: *{details.total_cost / 100:.2f} tc*'
            f' | {funcs.to_kyiv_str(order.created_at)}'
            f' | {glob.MOFFER_TEXT}: _{funcs.escape_markdown_v2(order.description)}_'
        )

    return '\n\n'.join(moffer_list) if moffer_list else None


async def get_material_order(order_code: str) -> Optional[MaterialOrder]:
    return await repo.get_material_order(order_code)


async def calculate_material_order_cost_details(
        material_name: str, quantity: int, offered_cost: int
) -> MaterialOrderCostDetailsDTO:
    rate_price = await get_material_price(material_name)
    offered_price = offered_cost / quantity
    rate_cost = round(quantity * rate_price)
    single_tax = round(glob.SINGLE_TAX * rate_cost)
    msend_tax = round(glob.MSEND_TAX * offered_cost)
    total_cost = offered_cost + single_tax + msend_tax

    return MaterialOrderCostDetailsDTO(
        rate_price=rate_price,
        offered_price=offered_price,
        rate_cost=rate_cost,
        single_tax=single_tax,
        msend_tax=msend_tax,
        total_cost=total_cost
    )


""" Minvo """

async def get_minvo_details(order: MaterialOrder) -> Optional[str]:
    details: MaterialOrderCostDetailsDTO = await calculate_material_order_cost_details(
        order.material_name, order.quantity, order.offered_cost
    )
    return (f'*{glob.MINVO_MAT_ORDER}* `#{order.code}`\n_{glob.MINVO_INVOICE}_'
            f'\n\n{glob.MINVO_SENDER}: {get_formatted_name(await get_member(order.sender_id), ping=True)}'
            f'\n{glob.MINVO_RECEIVER}: {get_formatted_name(await get_member(order.receiver_id), ping=True)}'
            f'\n\n{glob.MINVO_YOU_SEND}: *{order.quantity} {order.material_name}{await get_emoji(order.material_name)}*'
            f'\n{glob.MINVO_YOU_RECEIVE}: *{order.offered_cost / 100:.2f} tc*'
            f'\n\n{glob.MINVO_BUYER_PAYS}: {details.total_cost / 100:.2f} tc'
            f'\n{glob.MINVO_SINGLE_TAX_TEXT}: {details.single_tax / 100:.2f} tc ({int(glob.SINGLE_TAX * 100)}%)'
            f'\n{glob.MINVO_MSEND_TAX_TEXT}: {details.msend_tax / 100:.2f} tc ({int(glob.MSEND_TAX * 100)}%)'
            f'\n\n{glob.MINVO_RATE_PRICE}: {details.rate_price / 100:.7f} tc'
            f'\n{glob.MINVO_YOUR_PRICE}: {details.offered_price / 100:.7f} tc'
            f'\n\n{glob.MINVO_DESCRIPTION}: _{order.description}_')


async def get_minvos_page(user_id: int) -> Optional[str]:
    orders: list[MaterialOrder] = await repo.get_sender_material_orders(user_id)
    if not orders or len(orders) == 0:
        return f'_{glob.MINVO_EMPTY}_'

    minvo_list = []
    for order in orders:
        receiver = await get_member(order.receiver_id)
        details = await calculate_material_order_cost_details(order.material_name, order.quantity, order.offered_cost)
        minvo_list.append(
            f'`#{order.code}`'
            f' | {glob.MINVO_TO}: {get_formatted_name(receiver, ping=True)}'
            f' | *{order.quantity} {order.material_name}{await get_emoji(order.material_name)}*'
            f' | {glob.MINVO_COST}: *{order.offered_cost / 100:.2f} tc*'
            f' ({glob.MINVO_TAX_TEXT}: +{(details.single_tax + details.msend_tax) / 100:.2f} tc)'
            f' | {funcs.to_kyiv_str(order.created_at)}'
            f' | {glob.MINVO_TEXT}: _{funcs.escape_markdown_v2(order.description)}_'
        )

    return '\n\n'.join(minvo_list) if minvo_list else None


""" SFS Alert """


async def get_sfs_alert_message(chat_id: int) -> Optional[Message]:
    return sfs_alert_pins.get(chat_id)


async def pin_sfs_alert(chat_id: int, message: Message):
    await message.pin(disable_notification=True)
    sfs_alert_pins[chat_id] = message


async def unpin_sfs_alert(message: Message):
    await message.unpin()
    del sfs_alert_pins[message.chat.id]


""" Other """


async def reset_tpay_available():
    return await repo.reset_tpay_available()


async def reset_tbox_available():
    return await repo.reset_tbox_available()


async def payout_profits():
    for a in await repo.get_all_artifacts():
        profit_rate = await _get_artifact_profit_rate(a.type_)
        owner = await get_member(a.owner_id)
        creator = await get_member(a.creator_id)

        await _profit_business_account(
            member=owner,
            transfer=round(profit_rate * a.investment),
            profit_type=ProfitType.ARTIFACT_OWNER,
            artifact_id=a.artifact_id
        )

        # only if the creator was not unreg from ticketonomics
        # only if the owner is not the creator of the artifact
        if creator is not None and creator.user_id != owner.user_id:
            await _profit_business_account(
                member=creator,
                transfer=a.get_owner_profit(),
                profit_type=ProfitType.ARTIFACT_CREATOR,
                artifact_id=a.artifact_id
            )


async def payout_salaries(lsp_plan_date: datetime):
    employees = await repo.get_employees()

    if employees is None:
        await repo.set_salary_paid_out(
            plan_date=funcs.to_iso_z(lsp_plan_date),
            fact_date=funcs.utcnow_str()
        )
        return

    for e in employees:
        if e.salary <= 0:
            continue

        member = await get_member(e.user_id)
        if member is None:
            continue

        await _add_tickets(
            member=member,
            amount=e.salary,
            txn_type=TicketTxnType.SALARY,
            description=TicketTxnType.SALARY
        )

    await repo.set_salary_paid_out(
        plan_date=funcs.to_iso_z(lsp_plan_date),
        fact_date=funcs.utcnow_str()
    )


async def is_hired(user_id: int, position: str) -> bool:
    return await repo.get_employee(user_id, position) is not None


async def is_gem(material_name: str) -> bool:
    return any(material_name == g.name for g in await get_gems_list())


async def is_intermediate(material_name: str) -> bool:
    return any(material_name == im.name for im in await get_intermediates_list())


async def is_artifact_template(material_name: str) -> bool:
    return any(material_name == at.name for at in await get_artifact_templates_list())


""" Private """


async def _get_infl_rate_adjustments(price: float) -> (float, float, float):
    lpr = await repo.get_last_rate_history()

    if lpr is None:
        raise RuntimeError('No last price reset found!')

    return price * lpr.inflation * lpr.fluctuation, lpr.inflation, lpr.fluctuation


async def _find_recipe(name: str) -> Optional[Recipe]:
    for r in await _get_recipes():
        if r.result.name == name:
            return r
    return None


async def _get_rand_gemstones() -> Ingredient:
    schema = funcs.perturb_probs(
        probs=await _get_gem_freq(),
        sigma=glob.GEM_FREQ_SIGMA
    )
    gem = random.choices(
        population=await get_gems_list(),
        weights=schema
    )[0]
    quantity = random.randint(
        glob.MIN_GEM_COUNT_TBOX,
        glob.MAX_GEM_COUNT_TBOX
    )

    return Ingredient(
        name=gem.name,
        quantity=quantity
    )


async def _get_artifact_profit_rate(artifact_type: ArtifactType) -> float:
    return (await _get_artifact_profits_dict())[artifact_type]
