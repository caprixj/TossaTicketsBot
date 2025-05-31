import functools
import random

from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, LinkPreviewOptions

import resources.const.glob as glob
from command.routed.util.states import MsellStates
from model.database import Member, Material
from resources.const.rands import crv_messages
from service import service_core as service
from command.routed.util.validations import validate_message, validate_user
from command.parser.keyboards.keyboards import tpay_keyboard, hide_keyboard, one_btn_keyboard, \
    msell_choose_material_keyboard, msell_confirmation_keyboard
from command.parser.core import cog
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from component.paged_viewer import page_generators
from component.paged_viewer.paged_viewer import PagedViewer, keep_paged_viewer
from model.types.ticketonomics_types import PNReal, NInt, UserID
from command.parser.types.com_list import CommandList as cl
from command.parser.types.target_type import CommandTargetType as ctt
from resources.funcs import funcs

router = Router()


@router.message(Command(cl.help.name))
async def help_(message: Message):
    await validate_user(message.from_user)
    await message.answer(
        text=glob.HELP_TEXT,
        parse_mode=ParseMode.MARKDOWN,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        reply_markup=hide_keyboard()
    )


@router.message(Command(cl.infm.name))
async def infm(message: Message):
    if not await validate_message(message):
        return

    cpr = await CommandParser(message, cog.pure()).parse()

    if not cpr.valid:
        return await message.answer(glob.COM_PARSER_FAILED)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    await message.answer(
        text=await service.infm(target_member),
        parse_mode=ParseMode.HTML,
        reply_markup=hide_keyboard()
    )


@router.message(Command(cl.bal.name))
async def bal(message: Message):
    if not await validate_message(message):
        return

    cpr = await CommandParser(message, cog.pure()).parse()

    if not cpr.valid:
        return await message.answer(glob.COM_PARSER_FAILED)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    await message.answer(
        text=await service.bal(target_member),
        reply_markup=hide_keyboard()
    )


@router.message(Command(cl.balm.name))
async def balm(message: Message):
    if not await validate_message(message):
        return

    cpr = await CommandParser(message, cog.pure()).parse()

    if not cpr.valid:
        return await message.answer(glob.COM_PARSER_FAILED)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    viewer = PagedViewer(
        title=f'{glob.BALM_TITLE}\n{glob.BALM_MEMBER}: {funcs.get_formatted_name(target_member)}',
        data_extractor=functools.partial(service.balm, target_member.user_id),
        page_generator=page_generators.balm,
        page_message=message,
        start_text=glob.BALM_START_TEXT,
        parse_mode=ParseMode.HTML
    )

    operation_id = await service.operation_manager.register(
        func=functools.partial(keep_paged_viewer, viewer)
    )

    await viewer.view(operation_id)


@router.message(Command(cl.tbox.name))
async def tbox(message: Message):
    if not await validate_message(message):
        return

    member = await service.get_member(message.from_user.id)
    if member.tbox_available == 0:
        return await message.answer(glob.TBOX_UNAVAILABLE_ERROR)

    await message.reply(
        text=glob.TBOX_TEXT,
        reply_markup=one_btn_keyboard(
            text=glob.OPEN_TBOX_BTN,
            callback_name=glob.TBOX_CALLBACK,
            sender_id=member.user_id
        )
    )


@router.message(Command(cl.tpay.name))
async def tpay(message: Message, callback_message: Message = None, fee_incorporated: bool = False):
    if not await validate_message(message):
        return

    cpr = await CommandParser(message, cog.tickets(PNReal, creator_required=False)).parse()

    if not cpr.valid:
        return await message.answer(glob.COM_PARSER_FAILED)

    receiver = await service.get_target_member(cpr)

    if receiver is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

    sender = await service.get_member(message.from_user.id)

    if sender.tpay_available == 0:
        return await message.answer(glob.TPAY_UNAVAILABLE_ERROR)

    if sender.user_id == receiver.user_id:
        return await message.answer(glob.SELF_TRANS_ERROR)

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


@router.message(Command(cl.msell.name))
async def msell(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        CommandOverload(private=True)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        if cpr.private_violation:
            await message.answer(glob.PRIVATE_VIOLATION)
        else:
            await message.answer(glob.COM_PARSER_FAILED)
        return

    keyboard_data = await service.msell_markup(message.from_user.id)

    await message.reply(
        text=glob.MSELL_TEXT,
        reply_markup=msell_choose_material_keyboard(
            keyboard_data=keyboard_data,
            sender_id=message.from_user.id
        )
    )


@router.message(StateFilter(MsellStates.waiting_for_quantity), F.chat.type == 'private')
async def msell_quantity(message: Message, state: FSMContext):
    data = await state.get_data()
    quantity_message_id = data['quantity_message_id']

    if not message.reply_to_message or message.reply_to_message.message_id != quantity_message_id:
        return

    if not message.text.isdigit() or int(message.text) <= 0:
        return await message.answer(glob.MSELL_QUANTITY_INVALID)

    quantity = int(message.text)
    material: Material = data['material']

    price = await service.get_material_price(material.name)

    revenue = round(price * quantity, 2)
    tax = round(glob.UNI_TAX * revenue, 2)
    income = revenue - tax

    await state.update_data(quantity=quantity, revenue=revenue, tax=tax)
    await state.set_state(MsellStates.waiting_for_confirmation)

    await message.answer(
        text=(f'{glob.MSELL_MATERIALS_TO_SELL}: *{quantity}*'
              f'\n{glob.MSELL_CHOSEN_MATERIAL}: {material.name}{material.emoji}'
              f'\n{glob.MSELL_PRICE}: {price:.7f} tc'
              f'\n\n{glob.MSELL_REVENUE}: {revenue:.2f} tc'
              f'\n{glob.MSELL_TAX}: {tax:.2f} tc _({int(glob.UNI_TAX * 100)}%)_'
              f'\n*{glob.MSELL_INCOME}: {income:.2f} tc*'),
        reply_markup=msell_confirmation_keyboard()
    )


@router.message(Command(cl.ltrans.name, cl.xltrans.name))
async def ltrans(message: Message):
    if not await validate_message(message):
        return

    com = funcs.get_command(message)
    target_member: Member

    if com == cl.xltrans.name:
        cpr = await CommandParser(message, cog.pure(creator_required=True)).parse()

        if not cpr.valid:
            return await message.answer(glob.COM_PARSER_FAILED)

        target_member = await service.get_target_member(cpr)

        if target_member is None:
            return await message.answer(glob.GET_MEMBER_FAILED)
    else:  # if co.command == cl.ltrans.name
        target_member = await service.get_member(message.from_user.id)

    viewer = PagedViewer(
        title=f'{glob.LTRANS_TITLE}\n{glob.LTRANS_MEMBER}: {funcs.get_formatted_name(target_member)}',
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
        return await message.answer(glob.COM_PARSER_FAILED)

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        return await message.answer(glob.GET_MEMBER_FAILED)

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


@router.message(Command(commands=[cl.topt.name, cl.topm.name]))
async def rating(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        # /c
        CommandOverload(oid='pure'),
        # /c <size:nint>
        CommandOverload(oid='size').add(glob.SIZE_ARG, NInt),
        # /c <%>
        CommandOverload(oid='percent').add_percent(),
        # /c <%> <size:nint>
        CommandOverload(oid='percent-size').add_percent().add(glob.SIZE_ARG, NInt),
        # /c <id>
        CommandOverload(oid='id').add_id(),
        # /c <id> <size:nint>
        CommandOverload(oid='id-size').add_id().add(glob.SIZE_ARG, NInt),
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await message.answer(glob.COM_PARSER_FAILED)

    command_name = funcs.get_command(message)
    if command_name == cl.topt.name:
        logic = service.topt
    elif command_name == cl.topm.name:
        logic = service.topm
    else:
        raise RuntimeError('No command match in rating handler')

    if cpr.overload.oid == 'pure':
        await message.answer(
            text=await logic(),
            reply_markup=hide_keyboard()
        )
    elif cpr.overload.oid == 'size':
        size = cpr.args[glob.SIZE_ARG]
        await message.answer(
            text=await logic(size=size),
            reply_markup=hide_keyboard()
        )
    elif cpr.overload.oid == 'percent':
        await message.answer(
            text=await logic(percent_mode=True),
            reply_markup=hide_keyboard()
        )
    elif cpr.overload.oid == 'percent-size':
        size = cpr.args[glob.SIZE_ARG]
        await message.answer(
            text=await logic(size, percent_mode=True),
            reply_markup=hide_keyboard()
        )
    elif cpr.overload.oid == 'id':
        await message.answer(
            text=await logic(id_mode=True),
            reply_markup=hide_keyboard()
        )
    elif cpr.overload.oid == 'id-size':
        size = cpr.args[glob.SIZE_ARG]
        await message.answer(
            text=await logic(size, id_mode=True),
            reply_markup=hide_keyboard()
        )


@router.message(Command(cl.tpool.name))
async def tpool(message: Message):
    if not await validate_message(message):
        return

    await message.answer(
        text=await service.tpool(),
        reply_markup=hide_keyboard()
    )


@router.message(Command(cl.rates.name))
async def rates(message: Message):
    if not await validate_message(message):
        return

    await message.answer(
        text=await service.rates(),
        reply_markup=hide_keyboard()
    )


@router.message(Command(cl.alert.name))
async def alert(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        CommandOverload(public=True)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        if cpr.public_violation:
            await message.answer(glob.PUBLIC_VIOLATION)
        else:
            await message.answer(glob.COM_PARSER_FAILED)
        return

    if await service.get_sfs_alert_message(message.chat.id) is None:
        sent_message = await message.answer(glob.SFS_ALERT_TEXT)
        await service.pin_sfs_alert(message.chat.id, sent_message)
    else:
        await message.reply(glob.SFS_ALERT_FAILED)


@router.message(Command(cl.unalert.name))
async def unalert(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        CommandOverload(public=True)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        if cpr.public_violation:
            await message.answer(glob.PUBLIC_VIOLATION)
        else:
            await message.answer(glob.COM_PARSER_FAILED)
        return

    pin_message = await service.get_sfs_alert_message(message.chat.id)
    if pin_message is None:
        await message.reply(glob.SFS_UNALERT_FAILED)
    else:
        await service.unpin_sfs_alert(pin_message)
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
        return await message.answer(glob.COM_PARSER_FAILED)

    response = await service.p(cpr.args[glob.PRICE_ARG])
    await message.answer(
        text=response,
        reply_markup=hide_keyboard()
    )


@router.message(Command(cl.anchor.name))
async def anchor(message: Message):
    if not await validate_message(message):
        return

    og = CommandOverloadGroup([
        CommandOverload(public=True)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        if cpr.public_violation:
            await message.answer(glob.PUBLIC_VIOLATION)
        else:
            await message.answer(glob.COM_PARSER_FAILED)
        return

    response = await service.anchor(message.from_user.id, message.chat.id)
    await message.answer(response)


@router.message(Command(cl.reg.name))
async def reg(message: Message, bot: Bot):
    og = CommandOverloadGroup([
        # /reg
        CommandOverload(),
        # <reply> /reg
        CommandOverload(reply=True)
    ], public=True)

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        if cpr.public_violation:
            await message.answer(glob.PUBLIC_VIOLATION)
        else:
            await message.answer(glob.COM_PARSER_FAILED)
        return

    target_member = await service.get_target_member(cpr)

    if target_member is None:
        response = False
        if cpr.overload.target_type == ctt.none:
            response = await service.create_member(message.from_user, message.chat.id)
        elif cpr.overload.target_type == ctt.reply:
            response = await service.create_member(message.reply_to_message.from_user, message.chat.id)

        if not response and not message.from_user.id == glob.CREATOR_USER_ID:
            return message.answer(_get_random_crv_message())

        await bot.send_message(
            chat_id=glob.CREATOR_USER_ID,
            text=(f'chat id: {message.chat.id}\n'
                  f'user id: {message.from_user.id}')
        )

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
    if await service.get_sfs_alert_message(message.chat.id) is not None:
        await message.reply(glob.SFS_ALERT_TRIGGER_RESPONSE)
        await message.answer_sticker(glob.CRYING_STICKER_FILE_ID)


@router.message(Command(cl.tag.name))
async def tag(message: Message):
    og = CommandOverloadGroup([
        CommandOverload().add(glob.USER_ID_ARG, UserID)
    ])

    cpr = await CommandParser(message, og).parse()

    if not cpr.valid:
        return await message.answer(glob.COM_PARSER_FAILED)

    user_id = cpr.args[glob.USER_ID_ARG]
    await message.answer(
        text=f"[{glob.TAG_TEXT}](tg://user?id={user_id})",
        parse_mode=ParseMode.MARKDOWN
    )


def _get_random_crv_message() -> str:
    return crv_messages[random.randint(0, len(crv_messages) - 1)]
