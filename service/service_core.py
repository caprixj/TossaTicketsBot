import copy
import random
from datetime import datetime
from typing import Optional, List, Any

import aiofiles
import yaml
from aiogram.types import User, Message

import resources.const.glob as glob
from command.parser.results.parser_result import CommandParserResult
from command.parser.types.target_type import CommandTargetType as ctt
from model.database import Award, AwardMemberJunction, Member, AddtTransaction, DeltTransaction, TpayTransaction, \
    Recipe, Ingredient, Artifact, Material
from model.database.transactions import BusinessProfitTransaction, MaterialTransaction
from model.dto import AwardDTO, LTransDTO, TransactionResultDTO
from model.types import TransactionResultErrors as TRE, TicketTransactionType, ArtifactType
from model.types.profit_type import ProfitType
from model.types.transaction_types import MaterialTransactionType
from repository.ordering_type import OrderingType
from repository import repository_core as repo
from resources.funcs import funcs
from resources.sql import scripts
from service.operation_manager import ServiceOperationManager
from resources.funcs.funcs import get_formatted_name, get_fee, get_current_datetime, strdate, get_materials_yaml

operation_manager: ServiceOperationManager = ServiceOperationManager()
_recipes: list[Recipe] = list()
_materials: list[Material] = list()
_gem_freq: dict[str, float] = dict()
_artifact_profit: dict[str, float] = dict()
alert_pin: Optional[Message] = None

""" Global Getters """


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


async def execute_sql(query: str) -> (bool, str):
    return await repo.execute_external(query)


async def _add_tickets(member: Member, tickets: float, transaction_type: TicketTransactionType,
                       description: str = None):
    member.tickets = round(member.tickets + tickets, 2)
    time = get_current_datetime()

    await repo.update_member_tickets(member)
    await repo.insert_addt(AddtTransaction(
        user_id=member.user_id,
        tickets=tickets,
        time=time,
        description=description,
        type_=transaction_type
    ))


async def _delete_tickets(member: Member, tickets: float, transaction_type: TicketTransactionType,
                          description: str = None):
    member.tickets = round(member.tickets - tickets, 2)
    time = get_current_datetime()

    await repo.update_member_tickets(member)
    await repo.insert_delt(DeltTransaction(
        user_id=member.user_id,
        tickets=tickets,
        time=time,
        description=description,
        type_=transaction_type
    ))


async def _set_tickets(member: Member, tickets: float, transaction_type: TicketTransactionType,
                       description: str = None):
    if member.tickets == tickets:
        return

    time = get_current_datetime()

    if tickets > member.tickets:
        await repo.insert_addt(AddtTransaction(
            user_id=member.user_id,
            tickets=tickets - member.tickets,
            time=time,
            description=description,
            type_=transaction_type
        ))
    else:
        await repo.insert_delt(DeltTransaction(
            user_id=member.user_id,
            tickets=member.tickets - tickets,
            time=time,
            description=description,
            type_=transaction_type
        ))

    member.tickets = tickets
    await repo.update_member_tickets(member)


async def _profit_business_account(member: Member, transfer: float, profit_type: ProfitType, artifact_id: int):
    member.business_account = round(member.business_account + transfer, 2)
    date = get_current_datetime()

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
            f"\n{glob.INFM_PERSONAL}: {'+' if m.tickets > 0 else str()}{m.tickets:.2f}"
            f"\n{glob.INFM_BUSINESS}: {'+' if m.business_account > 0 else str()}{m.business_account:.2f}"
            f"\n{glob.INFM_TRANS_AVAILABLE}: {m.tpay_available}"
            f"\n{glob.INFM_TBOX_AVAILABLE}: {m.tbox_available}")


async def bal(m: Member) -> str:
    name = get_formatted_name(member=m, ping=True)
    sign = '+' if m.tickets > 0 else str()
    return (f"{glob.BAL_NAME}: {name}"
            f"\n{glob.BAL_PERSONAL}: {sign}{m.tickets:.2f}"
            f"\n{glob.BAL_BUSINESS}: {sign}{m.business_account:.2f}"
            f"\n{glob.BAL_TPAY_AVAILABLE}: {m.tpay_available}"
            f"\n{glob.BAL_TBOX_AVAILABLE}: {m.tbox_available}")


async def balm(user_id: int) -> list[Ingredient]:
    return await repo.get_all_member_materials(user_id)


async def tbox(user_id: int) -> str:
    member = await get_member(user_id)

    if member.tbox_available == 0:
        return glob.TBOX_UNAVAILABLE_ERROR

    gems = await _get_rand_gemstones()
    await repo.spend_tbox_available(member.user_id)
    await repo.add_member_material(user_id, gems)
    await repo.insert_material_transaction(MaterialTransaction(
        receiver_id=user_id,
        type_=MaterialTransactionType.tbox,
        material_name=gems.name,
        quantity=gems.quantity,
        date=get_current_datetime()
    ))

    return (f"*{glob.TBOX_OPENED_TEXT}*\n"
            f"{glob.TBOX_MEMBER}: {get_formatted_name(member)}\n\n"
            f"+{gems.quantity}{await get_emoji(gems.name)} ({gems.name})")


async def tpay(sender: Member, receiver: Member, transfer: float, description: str = None) -> TransactionResultDTO:
    fee = await get_fee(transfer)
    total = transfer + fee

    if total > sender.tickets:
        return TransactionResultDTO(TRE.insufficient_funds)

    current_datetime = get_current_datetime()

    # sender: -transfer -tpay_available
    sender.tickets -= transfer
    await repo.spend_tpay_available(sender.user_id)
    await repo.update_member_tickets(sender)
    await repo.insert_delt(DeltTransaction(
        user_id=sender.user_id,
        tickets=transfer,
        time=current_datetime,
        description=description,
        type_=TicketTransactionType.tpay
    ))

    # sender: -fee
    sender.tickets -= fee
    await repo.update_member_tickets(sender)
    await repo.insert_delt(DeltTransaction(
        user_id=sender.user_id,
        tickets=fee,
        time=current_datetime,
        description=description,
        type_=TicketTransactionType.tpay_tax
    ))

    # receiver: +transfer
    receiver.tickets += transfer
    await repo.update_member_tickets(receiver)
    await repo.insert_addt(AddtTransaction(
        user_id=receiver.user_id,
        tickets=transfer,
        time=current_datetime,
        description=description,
        type_=TicketTransactionType.tpay
    ))

    # save tpay transaction
    await repo.insert_tpay(TpayTransaction(
        sender_id=sender.user_id,
        receiver_id=receiver.user_id,
        transfer=transfer,
        fee=fee,
        time=current_datetime,
        description=description
    ))

    return TransactionResultDTO(valid=True)


async def ltrans(user_id: int) -> LTransDTO:
    return await repo.get_transaction_stats(user_id)


async def laward(user_id: int) -> Optional[List[AwardDTO]]:
    return await repo.get_awards(user_id)


async def topt(size: int = 0, percent_mode: bool = False, id_mode: bool = False) -> str:
    sized = size != 0

    if sized:
        order = OrderingType.DESC if size > 0 else OrderingType.ASC
        members = await repo.get_members_by_tickets_limited(order, abs(size))
        result = f'{glob.TOPT_DESC if size > 0 else glob.TOPT_ASC}'
    else:
        order = str()
        members = await repo.get_members_by_tickets()
        result = f'{glob.TOPT_DESC} {glob.TOPT_FULL}'

    total_tickets = await repo.get_sum_tickets()
    result += f"\n{glob.TOPT_TICKETS_TOTAL}: {total_tickets:.2f} tc\n\n"

    for i, m in enumerate(members):
        name = get_formatted_name(Member(
            username=m.username,
            first_name=m.first_name,
            last_name=m.last_name
        ))

        iterator = str()
        if i < 3 and (not sized or order == OrderingType.DESC):
            if i == 0:
                iterator = '🥇'
            elif i == 1:
                iterator = '🥈'
            elif i == 2:
                iterator = '🥉'
        else:
            iterator = f'{i + 1}.'

        if percent_mode:
            value = f'{m.tickets / total_tickets * 100:.2f}%' \
                if m.tickets > 0 else glob.TOPT_BANKRUPT
        else:
            sign = '+' if m.tickets > 0 else str()
            value = f'{sign}{m.tickets:.2f}'

        uid = f'[{m.user_id}] ' if id_mode else str()

        result += f'{iterator} {uid}( {value} )  {name[:32]}\n'

        if i == 2:
            result += '\n'

    return result


async def tpool() -> str:
    personal_tpool = await get_total_tickets()
    business_tpool = await get_business_tpool()
    artifact_tpool = await get_artifact_tpool()
    material_tpool = await get_material_tpool()

    nbt_tpool = await get_nbt_tpool()
    total_tpool = await get_tpool()

    return (f'{glob.TPOOL_PERSONAL}: {personal_tpool:.2f} tc'
            f'\n{glob.TPOOL_BUSINESS}: {business_tpool:.2f} tc'
            f'\n{glob.TPOOL_ARTIFACT}: {artifact_tpool:.2f} tc'
            f'\n{glob.TPOOL_MATERIAL}: {material_tpool:.2f} tc'
            f'\n\n{glob.TPOOL_NBT}: {nbt_tpool:.2f} tc'
            f'\n*{glob.TPOOL_TOTAL}: {total_tpool:.2f} tc*')


async def rates() -> str:
    rh = await repo.get_last_rate_history()

    gem_rates_view = str()
    for name, rate in (await repo.get_gem_prices_dict()).items():
        gem_rates_view += f'\n{await get_emoji(name)}*{name}*: {rate:.7f} tc'

    return (f'*\n{glob.RATES_REAL_INFL}: {(rh.inflation * rh.fluctuation - 1) * 100:.2f}%*'
            f'\n\n{glob.RATES_PURE_INFL}: {(rh.inflation - 1) * 100:.2f}%'
            f'\n{glob.RATES_FLUCT}: {(rh.fluctuation - 1) * 100:.2f}%'
            f'\n{gem_rates_view}')


async def p(price: float) -> str:
    adjusted_price, inflation, fluctuation = await _get_infl_rate_adjustments(price)
    return (f'{glob.P_BASE_PRICE}:\n{price:.2f} tc\n'
            f'\n{glob.P_ADJUSTED_PRICE}: {adjusted_price:.2f} tc'
            f'\n{glob.P_INFLATION}: {(inflation - 1) * 100:.3f}%'
            f'\n{glob.P_FLUCTUATION}: {(fluctuation - 1) * 100:.3f}%')


""" Creator Interfaces """


async def addt(member: Member, tickets: float, description: str = None) -> None:
    await _add_tickets(member, tickets, TicketTransactionType.creator, description)


async def delt(member: Member, tickets: float, description: str = None) -> None:
    await _delete_tickets(member, tickets, TicketTransactionType.creator, description)


async def sett(member: Member, tickets: float, description: str = None) -> None:
    await _set_tickets(member, tickets, TicketTransactionType.creator, description)


async def award(m: Member, a: Award, issue_date: str):
    if a.payment > 0:
        await pay_award(
            member=m,
            payment=a.payment,
            description=a.award_id
        )

    payment = f'\n{glob.AWARD_PAYMENT}: <b>{a.payment:.2f} tc</b>' \
        if a.payment > 0 else str()

    return (f"{glob.AWARD_SUCCESS}"
            f"\n\n<b>{a.name}</b>"
            f"\n\nid: <b>{a.award_id}</b>"
            f"{payment}"
            f"\n{glob.AWARD_ISSUED}: <b>{issue_date}</b>"
            f"\n\n<b>{glob.AWARD_STORY}</b>: <i>{a.description}</i>")


async def hire(user_id: int, position: str):
    await repo.insert_employee(
        user_id=user_id,
        position=position,
        hired_date=get_current_datetime()
    )


async def fire(user_id: int, position: str) -> bool:
    employee = await repo.get_employee(user_id, position)

    if employee is None:
        return False
    else:
        await repo.insert_employment_history(employee, get_current_datetime())
        await repo.delete_employee(user_id, position)
        return True


async def unreg(m: Member):
    await _set_tickets(
        member=m,
        tickets=0,
        transaction_type=TicketTransactionType.creator,
        description='unreg'
    )
    await repo.delete_member(m.user_id)


""" Get """


async def get_member(user_id: int) -> Optional[Member]:
    return await repo.get_member_by_user_id(user_id)


async def get_target_member(cpr: CommandParserResult) -> Optional[Member]:
    if cpr.overload.target_type == ctt.none:
        user_id = cpr.message.from_user.id
        return await repo.get_member_by_user_id(user_id)
    elif cpr.overload.target_type == ctt.reply:
        user_id = cpr.message.reply_to_message.from_user.id
        return await repo.get_member_by_user_id(user_id)
    elif cpr.overload.target_type == ctt.username:
        return await repo.get_member_by_username(cpr.args[glob.USERNAME_ARG])
    elif cpr.overload.target_type == ctt.user_id:
        return await repo.get_member_by_user_id(cpr.args[glob.USER_ID_ARG])


async def get_award(cpr: CommandParserResult) -> Optional[Award]:
    return await repo.get_award(cpr.args[glob.AWARD_ID_ARG])


async def get_job_names(user_id: float) -> Optional[List[str]]:
    return await repo.get_employee_position_names(user_id)


async def get_tpool() -> float:
    return sum([
        await get_total_tickets(),
        await get_business_tpool(),
        await get_artifact_tpool(),
        await get_material_tpool()
    ])


async def get_nbt_tpool() -> float:
    return await repo.get_nbt()


async def get_total_tickets() -> float:
    return await repo.get_sum_tickets()


async def get_business_tpool() -> float:
    return await repo.get_sum_business_accounts()


async def get_artifact_tpool() -> float:
    return sum(a.age_multiplier() * a.investment for a in await repo.get_all_artifacts())


async def get_material_tpool() -> float:
    raw_mtpool = await get_gc_value(
        await get_mpool_gem_counts()
    )

    artifact_mtpool = sum([
        await get_artifact_creation_price(a)
        for a in await repo.get_all_artifacts()
    ])

    return round(artifact_mtpool + (1 - glob.UNI_TAX) * raw_mtpool, 2)


async def get_artifact_price(a: Artifact) -> float:
    return a.age_multiplier() * a.investment + await get_artifact_creation_price(a)


async def get_artifact_creation_price(a: Artifact) -> float:
    return await get_gc_value(
        await get_gem_counts(
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
    gem_prices = await repo.get_gem_prices_dict()
    return sum(
        count * gem_prices[name]
        for name, count in gem_counts.items()
    )


async def get_gem_counts(r: Recipe) -> dict[str, float]:
    gem_counts = {g.name: 0. for g in await get_gems_list()}
    all_inner_gc = []

    for ingr in r.ingredients:
        norm = ingr.quantity / r.result.quantity
        if ingr.name in gem_counts:
            gem_counts[ingr.name] = norm
        else:
            inner_gc = await get_gem_counts(
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


async def get_mpool_gem_counts() -> dict[str, float]:
    mpool_gem_counts = {g.name: 0. for g in await get_gems_list()}

    for mat_name, mat_count in (await repo.get_each_material_count()).items():
        mat_rank = await get_material_rank(mat_name)
        if mat_rank == 1:
            mpool_gem_counts[mat_name] += mat_count
        else:
            r = await _find_recipe(mat_name)
            for g_name, g_count in (await get_gem_counts(r)).items():
                mpool_gem_counts[g_name] += mat_count * g_count * (glob.MAT_RANK_DEVAL ** (mat_rank - 1))

    return mpool_gem_counts


async def get_emoji(material_name: str) -> str:
    for m in await _get_materials():
        if m.name == material_name:
            return m.emoji


async def get_material_name(emoji: str) -> str:
    for m in await _get_materials():
        if m.emoji == emoji:
            return m.name


async def get_sold_items_count_today(user_id: int) -> int:
    return await repo.get_sold_items_count_today(user_id)


async def get_material_price(material_name: str) -> float:
    return await repo.get_material_price(material_name)


""" Member """


async def create_member(user: User) -> None:
    await repo.insert_member(Member(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    ))


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


async def issue_award(am: AwardMemberJunction) -> bool:
    return await repo.insert_award_member(am)


async def pay_award(member: Member, payment: float, description: str):
    await _add_tickets(member, payment, TicketTransactionType.award, description)


""" Msell """


async def msell_markup(user_id: int) -> list[list[str]]:
    materials = await repo.get_all_member_materials(user_id)

    # dict[str, int]
    gemstone_buttons = {}
    intermediates_buttons = {}
    artifact_templates_buttons = {}

    for ing in materials:
        btn = f'{await get_emoji(ing.name)} {ing.quantity}\n'
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
        btn_count = int(len(button_group) / glob.MSELL_BTN_ROW_LIMIT) + 1
        rows = list()
        for i in range(0, btn_count):
            beg = glob.MSELL_BTN_ROW_LIMIT * i
            end = glob.MSELL_BTN_ROW_LIMIT * (i + 1)
            rows.append(button_group[beg:end])
        return rows

    return list(filter(bool, [
        *_split_into_rows(gemstones_group),
        *_split_into_rows(intermediates_group),
        *_split_into_rows(artifact_templates_group)
    ]))


async def msell_transaction(data: dict[str, Any]):
    user_id: int = data['user_id']
    material: Material = data['material']
    quantity: int = data['quantity']
    revenue: float = data['revenue']
    tax: float = data['tax']
    member = await get_member(user_id)
    current_datetime = get_current_datetime()

    # -transaction -materials
    diff = Ingredient(material.name, quantity)
    await repo.spend_tpay_available(user_id)
    await repo.spend_member_material(user_id, diff)
    await repo.insert_material_transaction(MaterialTransaction(
        sender_id=user_id,
        type_=MaterialTransactionType.nbt,
        material_name=material.name,
        quantity=quantity,
        transfer=revenue - tax,
        tax=tax,
        date=current_datetime
    ))

    # +transfer
    member.tickets = round(member.tickets + revenue, 2)
    await repo.update_member_tickets(member)
    await repo.insert_addt(AddtTransaction(
        user_id=user_id,
        tickets=revenue,
        time=current_datetime,
        description=TicketTransactionType.nbt,
        type_=TicketTransactionType.nbt
    ))

    # -tax
    member.tickets = round(member.tickets - tax, 2)
    await repo.update_member_tickets(member)
    await repo.insert_delt(DeltTransaction(
        user_id=user_id,
        tickets=tax,
        time=current_datetime,
        description=TicketTransactionType.nbt_tax,
        type_=TicketTransactionType.nbt_tax
    ))


""" Other """


async def reset_tpay_available() -> (bool, str):
    return await repo.execute_external(scripts.RESET_MEMBER_TPAY_AVAILABLE)


async def reset_tbox_available() -> (bool, str):
    return await repo.execute_external(scripts.RESET_MEMBER_TBOX_AVAILABLE)


async def payout_profits():
    for a in await repo.get_all_artifacts():
        profit_rate = await _get_artifact_profit_rate(a.type_)
        owner = await get_member(a.owner_id)
        creator = await get_member(a.creator_id)

        await _profit_business_account(
            member=owner,
            transfer=round(profit_rate * a.investment, 2),
            profit_type=ProfitType.artifact_owner,
            artifact_id=a.artifact_id
        )

        # only if creator was not unreg from ticketonomics
        # only if the owner is not the creator of the artifact
        if creator is not None and creator.user_id != owner.user_id:
            await _profit_business_account(
                member=creator,
                transfer=a.get_owner_profit(),
                profit_type=ProfitType.artifact_creator,
                artifact_id=a.artifact_id
            )


async def payout_salaries(lsp_plan_date: datetime):
    employees = await repo.get_employees()

    if employees is None:
        await repo.set_salary_paid_out(
            plan_date=strdate(lsp_plan_date),
            fact_date=strdate(datetime.now())
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
            tickets=e.salary,
            transaction_type=TicketTransactionType.salary,
            description=TicketTransactionType.salary
        )

    await repo.set_salary_paid_out(
        plan_date=strdate(lsp_plan_date),
        fact_date=strdate(datetime.now())
    )


async def is_hired(user_id: float, position: str) -> bool:
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


async def get_formatted_material_name(material_name: str) -> str:
    if material_name:
        return material_name.replace('_', ' ')


async def _get_artifact_profit_rate(artifact_type: ArtifactType) -> float:
    return (await _get_artifact_profits_dict())[artifact_type]
