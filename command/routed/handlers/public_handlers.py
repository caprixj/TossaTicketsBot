import functools

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, LinkPreviewOptions

import resources.const.glob as glob
from model.types.router_filters import TextFilter
from service import service_core as service
from command.routed.handlers.validations import validate_message
from command.routed.keyboards.keyboards import tpay_keyboard, hide_keyboard
from command.parser.core import cog
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from component.paged_viewer import page_generators
from component.paged_viewer.paged_viewer import PagedViewer, keep_paged_viewer
from model.types.ticketonomics_types import PNReal, NInt
from command.parser.types.com_list import CommandList as cl
from command.parser.types.target_type import CommandTargetType as ctt
from model.types.transaction_result_errors import TransactionResultErrors as tre
from resources.funcs import funcs
from service.price_manager import adjust_tickets_amount

router = Router()


@router.message(TextFilter(r'^[дД]+[аА]+[.]*[!]*[?]*$', regex=True))
async def da(message: Message):
    await message.answer(f'пиз{message.text}')


@router.message(TextFilter(r'^[нН]+[єЄ]+[.]*[!]*[?]*$', regex=True))
async def nie_ua(message: Message):
    await message.answer(f'рука в гав{message.text}!')


@router.message(TextFilter(r'^[нН]+[еЕ]+[.]*[!]*[?]*$', regex=True))
async def nie_ru(message: Message):
    await message.answer(f'рука в гов{message.text}!')


@router.message(Command(cl.reg.name))
async def reg(message: Message):
    og = CommandOverloadGroup([
        # /reg
        CommandOverload(),
        # <reply> /reg
        CommandOverload(reply_required=True)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        if cpr.overload.target_type == ctt.none:
            await service.create_member(message.from_user)
        elif cpr.overload.target_type == ctt.reply:
            await service.create_member(message.reply_to_message.from_user)
        await message.answer(glob.REG_SUCCESS)
    else:
        if cpr.overload.target_type == ctt.none:
            await service.update_member(message.from_user, target_member)
            await message.answer(glob.REG_DENIED_CTT_NONE)
        elif cpr.overload.target_type == ctt.reply:
            await service.update_member(message.reply_to_message.from_user, target_member)
            await message.answer(glob.REG_DENIED_CTT_REPLY)


@router.message(Command(cl.rusni.name))
async def rusni(message: Message):
    await validate_message(message)
    await message.answer(glob.RUSNI_TEXT)


@router.message(Command(cl.help.name))
async def help_(message: Message):
    await validate_message(message)
    await message.answer(
        text=glob.HELP_TEXT,
        parse_mode=ParseMode.MARKDOWN,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        reply_markup=hide_keyboard(glob.HELP_HIDE_CALLBACK)
    )


@router.message(Command(cl.ltrans.name))
async def ltrans(message: Message):
    if not await validate_message(message):
        return

    cpr = await CommandParser(message, cog.pure()).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    viewer = PagedViewer(
        title=glob.LTRANS_TITLE,
        data_extractor=functools.partial(service.ltrans, target_member.user_id),
        page_generator=page_generators.ltrans,
        page_message=message,
        start_text=glob.LTRANS_START_TEXT,
        parse_mode=ParseMode.HTML
    )

    operation_id = await service.operation_manager.register(
        func=functools.partial(keep_paged_viewer, viewer)
    )

    await viewer.view(operation_id)


@router.message(Command(cl.laward.name))
async def laward(message: Message):
    if not await validate_message(message):
        return

    cpr = await CommandParser(message, cog.pure()).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    viewer = PagedViewer(
        title=glob.LAWARD_TITLE,
        data_extractor=functools.partial(service.laward, target_member.user_id),
        page_generator=page_generators.laward,
        page_message=message,
        parse_mode=ParseMode.HTML
    )

    operation_id = await service.operation_manager.register(
        func=functools.partial(keep_paged_viewer, viewer)
    )

    await viewer.view(operation_id)


@router.message(Command(cl.topt.name))
async def topt(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        # /topt
        CommandOverload(oid='pure'),
        # /topt <size:nint>
        CommandOverload(oid='size').add(glob.SIZE_ARG, NInt),
        # /topt <%>
        CommandOverload(oid='percent').add_percent(),
        # /topt <%> <size:nint>
        CommandOverload(oid='percent-size').add_percent().add(glob.SIZE_ARG, NInt),
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    if cpr.overload.oid == 'pure':
        await message.answer(
            text=await service.topt(),
            reply_markup=hide_keyboard(glob.TOPT_HIDE_CALLBACK)
        )
    elif cpr.overload.oid == 'size':
        size = cpr.args[glob.SIZE_ARG]
        await message.answer(
            text=await service.topt(size=size),
            reply_markup=hide_keyboard(glob.TOPT_HIDE_CALLBACK)
        )
    elif cpr.overload.oid == 'percent':
        await message.answer(
            text=await service.topt(percent=True),
            reply_markup=hide_keyboard(glob.TOPT_HIDE_CALLBACK)
        )
    else:  # cpr.overload.oid == 'percent-size'
        size = cpr.args[glob.SIZE_ARG]
        await message.answer(
            text=await service.topt(size, percent=True),
            reply_markup=hide_keyboard(glob.TOPT_HIDE_CALLBACK)
        )


@router.message(Command(cl.bal.name))
async def bal(message: Message):
    if not await validate_message(message):
        return

    cpr = await CommandParser(message, cog.pure()).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    name = funcs.get_formatted_name(member=target_member, ping=True)
    sign = '+' if target_member.tickets > 0 else str()
    response = (f"🪪 ім'я: {name}"
                f"\n💳 тікети: {sign}{target_member.tickets:.2f}"
                f"\n🔀 доступно транзакцій: {target_member.tpay_available}")

    await message.answer(response)


@router.message(Command(cl.infm.name))
async def infm(message: Message):
    if not await validate_message(message):
        return

    cpr = await CommandParser(message, cog.pure()).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    response = await service.infm(target_member.user_id)
    await message.answer(response, parse_mode=ParseMode.HTML)


@router.message(Command(cl.tpay.name))
async def tpay(message: Message, callback_message: Message = None, fee_incorporated: bool = False):
    if not await validate_message(message):
        return

    cpr = await CommandParser(message, cog.tickets(PNReal, creator_required=False)).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    receiver = await service.get_target_member(cpr)

    if receiver is None:
        await message.answer(glob.GET_MEMBER_FAILED)
        return

    sender = await service.get_member(message.from_user.id)

    if sender.tpay_available == 0:
        await message.answer(tre.tpay_unavailable)
        return

    description = cpr.args.get(glob.DESCRIPTION_ARG, None)

    # t - total, x - transfer, f - fee
    # -> (t, x, f)
    async def calculate_transfer(x: float) -> (float, float, float):
        if fee_incorporated:
            t_fi = x
            x_fi = await funcs.get_transfer_by_total(t_fi)
            return t_fi, x_fi, t_fi - x_fi
        else:
            f = await funcs.get_fee(x)
            return x + f, x, f

    total, transfer, fee = await calculate_transfer(cpr.args[glob.TICKETS_ARG])

    tpay_confirmation_text = (f'відправник: {funcs.get_formatted_name(sender, ping=True)}\n'
                              f'отримувач: {funcs.get_formatted_name(receiver, ping=True)}\n\n'
                              f'*загальна сума: {total:.2f}*\n'
                              f'сума переказу: {transfer:.2f}\n'
                              f'комісія: {fee:.2f} ({int(100 * glob.FEE_RATE)}%, min {glob.MIN_FEE:.2f})\n\n'
                              f'опис: _{description}_')

    operation_id = await service.operation_manager.register(
        func=functools.partial(service.tpay, sender, receiver, transfer, description),
        command_message=message
    )

    if fee_incorporated:
        await callback_message.edit_text(text=tpay_confirmation_text)
        await callback_message.edit_reply_markup(
            reply_markup=tpay_keyboard(
                operation_id=operation_id,
                sender_id=sender.user_id,
                fee_incorporated=False
            )
        )
    else:
        await message.answer(
            text=tpay_confirmation_text,
            reply_markup=tpay_keyboard(
                operation_id=operation_id,
                sender_id=sender.user_id,
                fee_incorporated=transfer > glob.MIN_FEE
            )
        )


@router.message(Command(cl.p.name))
async def p(message: Message):
    og = CommandOverloadGroup([
        # /p <price:pnreal>
        CommandOverload().add(glob.PRICE_ARG, PNReal)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    price = cpr.args[glob.PRICE_ARG]
    adjusted_price, inflation, fluctuation = await adjust_tickets_amount(price)
    await message.answer(f'базова вартість: {price:.2f} tc'
                         f'\nскорегована вартість: {adjusted_price:.2f} tc'
                         f'\nінфляція: {(inflation - 1) * 100:.3f}%'
                         f'\nпоточна флуктуація: {(fluctuation - 1) * 100:.3f}%')
