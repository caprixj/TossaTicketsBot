import functools

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, LinkPreviewOptions

import resources.const.glob as glob
from service import service_core as service
from command.routed.handlers.validations import validate_message, validate_user
from command.routed.keyboards.keyboards import tpay_keyboard, hide_keyboard
from command.parser.core import cog
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from component.paged_viewer import page_generators
from component.paged_viewer.paged_viewer import PagedViewer, keep_paged_viewer
from model.types.ticketonomics_types import PNReal, NInt, UserID
from command.parser.types.com_list import CommandList as cl
from command.parser.types.target_type import CommandTargetType as ctt
from model.types.transaction_result_errors import TransactionResultErrors as tre
from resources.funcs import funcs

router = Router()


@router.message(Command(cl.help.name))
async def help_(message: Message):
    await validate_user(message.from_user)
    await message.answer(
        text=glob.HELP_TEXT,
        parse_mode=ParseMode.MARKDOWN,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        reply_markup=hide_keyboard(glob.HELP_HIDE_CALLBACK)
    )


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

    await message.answer(
        text=await service.infm(target_member),
        parse_mode=ParseMode.HTML,
        reply_markup=hide_keyboard(glob.HELP_HIDE_CALLBACK)
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

    await message.answer(
        text=await service.bal(target_member),
        reply_markup=hide_keyboard(glob.HELP_HIDE_CALLBACK)
    )


@router.message(Command(cl.tbox.name))
async def tbox(message: Message):
    if not await validate_message(message):
        return

    #


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

    tpay_confirmation_text = (f'{glob.TPAY_SENDER}: {funcs.get_formatted_name(sender, ping=True)}\n'
                              f'{glob.TPAY_RECEIVER}: {funcs.get_formatted_name(receiver, ping=True)}\n\n'
                              f'*{glob.TPAY_TOTAL}: {total:.2f}*\n'
                              f'{glob.TPAY_AMOUNT}: {transfer:.2f}\n'
                              f'{glob.TPAY_TAX}: {fee:.2f} ({int(100 * glob.UNI_TAX)}%, min {glob.MIN_FEE:.2f})\n\n'
                              f'{glob.TPAY_DESCRIPTION}: _{description}_')

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
        title=f'{glob.LTRANS_TITLE}\nmember: {funcs.get_formatted_name(target_member)}',
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


@router.message(Command(cl.tpool.name))
async def tpool(message: Message):
    if not await validate_message(message):
        return

    personal_tpool = await service.get_total_tickets()
    business_tpool = await service.get_business_tpool()
    artifact_tpool = await service.get_artifact_tpool()
    material_tpool = await service.get_material_tpool()
    total_tpool = personal_tpool + business_tpool + artifact_tpool

    await message.answer(
        text=f'{glob.TPOOL_PERSONAL}: {personal_tpool:.2f} tc'
             f'\n{glob.TPOOL_BUSINESS}: {business_tpool:.2f} tc'
             f'\n{glob.TPOOL_ARTIFACT}: {artifact_tpool:.2f} tc'
             f'\n{glob.TPOOL_MATERIAL}: {material_tpool:.2f} tc'
             f'\n\n*{glob.TPOOL_TOTAL}: {total_tpool:.2f} tc*',
        reply_markup=hide_keyboard(glob.HELP_HIDE_CALLBACK)
    )


@router.message(Command(cl.alert.name))
async def alert(message: Message):
    if not await validate_message(message):
        return

    if service.alert_pin is None:
        sent_message = await message.answer(glob.SFS_ALERT_TEXT)
        await sent_message.pin(disable_notification=True)
        service.alert_pin = sent_message
    else:
        await message.reply(glob.SFS_ALERT_FAILED)


@router.message(Command(cl.unalert.name))
async def unalert(message: Message):
    if not await validate_message(message):
        return

    if service.alert_pin is None:
        await message.reply(glob.SFS_UNALERT_FAILED)
    else:
        await service.alert_pin.unpin()
        service.alert_pin = None
        await message.reply(glob.SFS_UNALERT_TEXT)


@router.message(Command(cl.rusni.name))
async def rusni(message: Message):
    await validate_message(message)
    await message.answer(glob.RUSNI_TEXT)


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

    response = await service.p(cpr.args[glob.PRICE_ARG])
    await message.answer(
        text=response,
        reply_markup=hide_keyboard(glob.HELP_HIDE_CALLBACK)
    )


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


""" Non-Commands """


@router.message(F.text.regexp(r'^[дД]+[аА]+[.]*[!]*[?]*$'))
async def da(message: Message):
    await message.answer(f'пиз{message.text}')


@router.message(F.text.regexp(r'^[нН]+[єЄ]+[.]*[!]*[?]*$'))
async def nie_ua(message: Message):
    await message.answer(f'рука в гав{message.text}!')


@router.message(F.text.regexp(r'^[нН]+[еЕ]+[.]*[!]*[?]*$'))
async def nie_ru(message: Message):
    await message.answer(f'рука в гов{message.text}!')


@router.message(F.text.regexp(r'сфс|СФС|sfs|SFS'))
async def sfs_alert_trigger(message: Message):
    if service.alert_pin is not None:
        await message.reply(glob.SFS_ALERT_TRIGGER_RESPONSE)
        await message.answer_sticker(glob.CRYING_STICKER_FILE_ID)


@router.message(Command('tag'))
async def tag(message: Message):
    og = CommandOverloadGroup([
        CommandOverload().add(glob.USER_ID_ARG, UserID)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        await message.answer(glob.COM_PARSER_FAILED)
        return

    nametag = cpr.args[glob.USER_ID_ARG]
    await message.answer(f"[tag](tg://user?id={nametag})", parse_mode=ParseMode.MARKDOWN)


@router.message()
async def _catch_all(message: Message):
    pass
