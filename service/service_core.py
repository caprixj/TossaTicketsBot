import copy
from datetime import datetime
from typing import Union, Optional, List

import aiofiles
import yaml
from aiogram.types import User, Message

import resources.const.glob as glob
from command.parser.results.parser_result import CommandParserResult
from command.parser.types.target_type import CommandTargetType as ctt
from model.database import Award, AwardMemberJunction, Member, AddtTransaction, DeltTransaction, TpayTransaction, \
    Recipe, Ingredient, Artifact, Material
from model.dto import AwardDTO, LTransDTO, TransactionResultDTO
from model.types import TransactionResultErrors as TRE, TransactionType
from repository.ordering_type import OrderingType
from repository import repository_core as repo
from service.operation_manager import ServiceOperationManager
from resources.funcs.funcs import get_formatted_name, get_fee, get_current_datetime, strdate, get_materials_yaml
from resources.sql.scripts import RESET_MEMBER_TPAY_AVAILABLE

operation_manager: ServiceOperationManager = ServiceOperationManager()
recipes: list[Recipe] = []
materials: list[Material] = []
alert_pin: Optional[Message] = None

""" General """


async def execute_sql(query: str) -> (bool, str):
    return await repo.execute_external(query)


async def _add_tickets(member: Member, tickets: float, transaction_type: TransactionType, description: str = None):
    member.tickets += tickets
    time = get_current_datetime()

    await repo.update_member_tickets(member)
    await repo.insert_addt(AddtTransaction(
        user_id=member.user_id,
        tickets=tickets,
        time=time,
        description=description,
        type_=transaction_type
    ))


async def _delete_tickets(member: Member, tickets: float, transaction_type: TransactionType, description: str = None):
    member.tickets -= tickets
    time = get_current_datetime()

    await repo.update_member_tickets(member)
    await repo.insert_delt(DeltTransaction(
        user_id=member.user_id,
        tickets=tickets,
        time=time,
        description=description,
        type_=transaction_type
    ))


async def _set_tickets(member: Member, tickets: float, transaction_type: TransactionType, description: str = None):
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


""" Interfaces """


async def topt(size: int = 0, percent: bool = False) -> str:
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

        if percent:
            value = f'{m.tickets / total_tickets * 100:.2f}%' \
                if m.tickets > 0 else glob.TOPT_BANKRUPT
        else:
            sign = '+' if m.tickets > 0 else str()
            value = f'{sign}{m.tickets:.2f}'

        result += f'{iterator} ( {value} )  {name[:32]}\n'

        if i == 2:
            result += '\n'

    return result


async def bal(m: Member) -> str:
    name = get_formatted_name(member=m, ping=True)
    sign = '+' if m.tickets > 0 else str()
    return (f"{glob.BAL_NAME}: {name}"
            f"\n{glob.BAL_PERSONAL}: {sign}{m.tickets:.2f}"
            f"\n{glob.BAL_BUSINESS}: {sign}{m.business_account:.2f}"
            f"\n{glob.BAL_TICKETS_AVAILABLE}: {m.tpay_available}")


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
            f"\n{glob.INFM_TRANS_AVAILABLE}: {m.tpay_available}")


async def addt(member: Member, tickets: float, description: str = None) -> None:
    await _add_tickets(member, tickets, TransactionType.creator, description)


async def delt(member: Member, tickets: float, description: str = None) -> None:
    await _delete_tickets(member, tickets, TransactionType.creator, description)


async def sett(member: Member, tickets: float, description: str = None) -> None:
    await _set_tickets(member, tickets, TransactionType.creator, description)


async def tpay(sender: Member, receiver: Member, transfer: float, description: str = None) -> TransactionResultDTO:
    fee = await get_fee(transfer)
    total = transfer + fee

    if total > sender.tickets:
        return TransactionResultDTO(TRE.insufficient_funds)

    time = get_current_datetime()

    # sender: -transfer -tpay_available
    sender.tickets -= transfer
    await repo.update_member_tickets(sender)
    await repo.spend_tpay_available(sender)
    await repo.insert_delt(DeltTransaction(
        user_id=sender.user_id,
        tickets=transfer,
        time=time,
        description=description,
        type_=TransactionType.tpay
    ))

    # sender: -fee
    sender.tickets -= fee
    await repo.update_member_tickets(sender)
    await repo.insert_delt(DeltTransaction(
        user_id=sender.user_id,
        tickets=fee,
        time=time,
        description=description,
        type_=TransactionType.tpay_fee
    ))

    # receiver: +transfer
    receiver.tickets += transfer
    await repo.update_member_tickets(receiver)
    await repo.insert_addt(AddtTransaction(
        user_id=receiver.user_id,
        tickets=transfer,
        time=time,
        description=description,
        type_=TransactionType.tpay
    ))

    # save tpay transaction
    await repo.insert_tpay(TpayTransaction(
        sender_id=sender.user_id,
        receiver_id=receiver.user_id,
        transfer=transfer,
        fee=fee,
        time=time,
        description=description
    ))

    return TransactionResultDTO(valid=True)


async def ltrans(user_id: int) -> LTransDTO:
    return await repo.get_transaction_stats(user_id)


async def laward(user_id: int) -> Optional[List[AwardDTO]]:
    return await repo.get_awards(user_id)


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


async def p(price: float) -> str:
    adjusted_price, inflation, fluctuation = await _get_infl_rate_adjustments(price)
    return (f'{glob.P_BASE_PRICE}:\n{price:.2f} tc\n'
            f'\n{glob.P_ADJUSTED_PRICE}: {adjusted_price:.2f} tc'
            f'\n{glob.P_INFLATION}: {(inflation - 1) * 100:.3f}%'
            f'\n{glob.P_FLUCTUATION}: {(fluctuation - 1) * 100:.3f}%')


async def unreg(m: Member):
    await _set_tickets(
        member=m,
        tickets=0,
        transaction_type=TransactionType.creator,
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


async def get_total_tpool() -> float:
    return sum([
        await get_total_tickets(),
        await get_business_tpool(),
        await get_artifact_tpool(),
        await get_material_tpool()
    ])


async def get_total_tickets() -> float:
    return await repo.get_sum_tickets()


async def get_business_tpool() -> float:
    return await repo.get_sum_business_accounts()


async def get_artifact_tpool() -> float:
    return sum(a.investment for a in await repo.get_all_artifacts())


async def get_material_tpool() -> float:
    raw_mtpool = await get_gc_value(
        await get_mpool_gem_counts()
    )

    artifact_mtpool = sum([
        await get_artifact_creation_price(a)
        for a in await repo.get_all_artifacts()
    ])

    return artifact_mtpool + raw_mtpool


async def get_artifact_price(a: Artifact) -> float:
    return a.investment + await get_artifact_creation_price(a)


async def get_artifact_creation_price(a: Artifact) -> float:
    return await get_gc_value(
        await get_gem_counts(
            await find_recipe(
                f'{a.type_}_artifact'
            )))


async def get_material_rank(material_name: str) -> int:
    rank = 2

    r = await find_recipe(material_name)
    if r is None:
        return 1

    for ingr in r.ingredients:
        if not any(ingr.name == m.name for m in await get_gems()):
            rank = max(rank, 1 + await get_material_rank(ingr.name))

    return rank


async def get_gems() -> list[Material]:
    return (await _get_materials())[:7]


async def get_gc_value(gem_counts: dict[str, float]) -> float:
    gem_prices = await repo.get_gem_prices_dict()
    return sum(
        count * gem_prices[name]
        for name, count in gem_counts.items()
    )


async def get_gem_counts(r: Recipe) -> dict[str, float]:
    gem_counts = {g.name: 0. for g in await get_gems()}
    all_inner_gc = []

    for ingr in r.ingredients:
        norm = ingr.quantity / r.result.quantity
        if ingr.name in gem_counts:
            gem_counts[ingr.name] = norm
        else:
            inner_gc = await get_gem_counts(
                await find_recipe(ingr.name)
            )
            for key, value in inner_gc.items():
                inner_gc[key] = value * norm
            all_inner_gc.append(inner_gc)

    if all_inner_gc:
        result = {g.name: 0. for g in await get_gems()}
        all_gc = [gem_counts, *all_inner_gc]
        for pc in all_gc:
            for key, value in pc.items():
                result[key] += value
        return result
    else:
        return gem_counts


async def get_mpool_gem_counts() -> dict[str, float]:
    mpool_gem_counts = {g.name: 0. for g in await get_gems()}

    for mat_name, mat_count in (await repo.get_each_material_count()).items():
        mat_rank = await get_material_rank(mat_name)
        if mat_rank == 1:
            mpool_gem_counts[mat_name] += mat_count
        else:
            r = await find_recipe(mat_name)
            for g_name, g_count in (await get_gem_counts(r)).items():
                mpool_gem_counts[g_name] += mat_count * g_count * (glob.MAT_RANK_DEVAL ** (mat_rank - 1))

    return mpool_gem_counts


""" Member """


async def create_member(value: Union[Member, User]) -> None:
    if isinstance(value, Member):
        await repo.insert_member(value)
    elif isinstance(value, User):
        member = Member(
            user_id=value.id,
            username=value.username,
            first_name=value.first_name,
            last_name=value.last_name
        )
        await repo.insert_member(member)
    else:
        raise TypeError()


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
    await _add_tickets(member, payment, TransactionType.award, description)


""" Other """


async def reset_tpay_available() -> (bool, str):
    return await repo.execute_external(RESET_MEMBER_TPAY_AVAILABLE)


async def payout_salaries(lsp_plan_date: datetime):
    employees = await repo.get_employees()

    if employees is None:
        await repo.set_salary_paid_out(
            plan_date=strdate(lsp_plan_date),
            fact_date=strdate(datetime.now())
        )
        return

    for e in employees:
        if e.salary != 0:
            await _add_tickets(
                member=await repo.get_member_by_user_id(e.user_id),
                tickets=e.salary,
                transaction_type=TransactionType.salary,
                description=TransactionType.salary
            )

    await repo.set_salary_paid_out(
        plan_date=strdate(lsp_plan_date),
        fact_date=strdate(datetime.now())
    )


async def is_hired(user_id: float, position: str) -> bool:
    return await repo.get_employee(user_id, position) is not None


async def find_recipe(name: str) -> Optional[Recipe]:
    for r in await _get_recipes():
        if r.result.name == name:
            return r
    return None


async def claim_bhf(user_id: int):
    bhf = 'banhammer_fragments'
    mm = await repo.get_member_material(user_id, bhf)
    q = 1 if mm is None else mm.quantity + 1
    await repo.upsert_member_material(user_id, Ingredient(bhf, q))


""" Private """


async def _get_recipes() -> List[Recipe]:
    global recipes

    if not recipes:
        async with aiofiles.open(glob.RECIPES_YAML_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(await f.read())

        recipes = [
            Recipe(
                result=Ingredient(**item['result']),
                ingredients=[Ingredient(**ingr) for ingr in item['ingredients']]
            ) for item in data
        ]

    return recipes


async def _get_materials() -> list[Material]:
    global materials

    if not materials:
        materials = await get_materials_yaml()

    return materials


async def _get_infl_rate_adjustments(price: float) -> (float, float, float):
    lpr = await repo.get_last_price_reset()

    if lpr is None:
        raise RuntimeError('No last price reset found!')

    return price * lpr.inflation * lpr.fluctuation, lpr.inflation, lpr.fluctuation
