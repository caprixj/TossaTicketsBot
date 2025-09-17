from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State

import resources.glob as glob
from command.util.validations import validate_message
from component.keyboards.keyboards import choose_material_keyboard
from command.parser.core.overload import CommandOverload, CommandOverloadGroup
from command.parser.core.parser import CommandParser
from command.parser.types.command_list import CommandList as CL
from component.keyboards.keyboards import confirmation_keyboard
from model.database.materials import Material, Ingredient
from model.types.custom.primitives import PNInt
from service import service_core as service
from service.cbdata.redis_stash import peek_payload


class MsellStates(StatesGroup):
    waiting_for_quantity = State()
    waiting_for_confirmation = State()


router = Router()


@router.message(Command(CL.msell.name))
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

    keyboard_data = await service.get_materials_markup(message.from_user.id)

    await message.reply(
        text=glob.MSELL_TEXT,
        reply_markup=await choose_material_keyboard(
            keyboard_data=keyboard_data,
            signature=glob.MSELL_QUANTITY_CALLBACK,
            user_id=message.from_user.id
        )
    )


@router.callback_query(F.data.startswith(glob.MSELL_QUANTITY_CALLBACK))
async def msell_quantity(callback: CallbackQuery, state: FSMContext):
    # (redis) get button's data
    data = await peek_payload(callback)
    if not data:
        return await callback.answer(glob.FLOW_EXPIRED, show_alert=True)

    # (core) process data
    emoji: str = data['emoji']
    quantity: int = data['quantity']
    reserved: int = data['reserved']
    user_id: int = data['user_id']
    material = Material(
        emoji=emoji,
        name=await service.get_formatted_material_name(
            await service.get_material_name(emoji)
        )
    )

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(
        f"{glob.MSELL_CHOSEN_MATERIAL_EMOJI}: *{material.name}{material.emoji} ({quantity - reserved})*"
    )
    await callback.message.answer(glob.MSELL_ASK_QUANTITY)

    # (fsm) pass flow's data and set the state
    await state.update_data(
        user_id=user_id,
        material=material,
        reserved=reserved
    )
    await state.set_state(MsellStates.waiting_for_quantity)

    await callback.answer()


@router.message(StateFilter(MsellStates.waiting_for_quantity))
async def msell_confirm(message: Message, state: FSMContext):
    # (fsm) get flow's data
    data = await state.get_data()
    if not data:
        return await message.answer(glob.FLOW_EXPIRED, show_alert=True)

    # (core) process data
    if not PNInt(message.text).validate():
        return await message.answer(glob.MSELL_QUANTITY_INVALID)

    quantity = int(message.text)
    user_id: int = data['user_id']
    material: Material = data['material']
    reserved: int = data['reserved']

    material_bal: Ingredient = await service.get_member_material(user_id, material.name)
    available = material_bal.quantity - reserved
    if material_bal is None or available < quantity:
        return await message.answer(glob.MSEND_QUANTITY_INSUFFICIENT)

    price = await service.get_material_price(material.name)

    revenue = round(price * quantity)
    single_tax = round(glob.SINGLE_TAX * revenue)
    msell_tax = round(glob.MSELL_TAX * revenue)
    income = revenue - single_tax - msell_tax

    # (fsm) pass flow's data and set the state
    await state.update_data(
        quantity=quantity,
        revenue=revenue,
        single_tax=single_tax,
        msell_tax=msell_tax
    )
    await state.set_state(MsellStates.waiting_for_confirmation)

    # (core) send a confirmation form
    await message.answer(
        text=(f'{glob.MSELL_MATERIALS_TO_SELL}: *{quantity}*'
              f'\n{glob.MSELL_CHOSEN_MATERIAL}: {material.name}{material.emoji}'
              f'\n{glob.MSELL_PRICE}: {price / 100:.7f} tc'
              f'\n\n{glob.MSELL_REVENUE}: {revenue / 100:.2f} tc'
              f'\n{glob.MSELL_SINGLE_TAX_TEXT}: {single_tax / 100:.2f} tc ({int(glob.SINGLE_TAX * 100)}%)'
              f'\n{glob.MSELL_MSELL_TAX_TEXT}: {msell_tax / 100:.2f} tc ({int(glob.MSELL_TAX * 100)}%)'
              f'\n*{glob.MSELL_INCOME}: {income / 100:.2f} tc*'),
        reply_markup=confirmation_keyboard(
            yes_cbdata=glob.MSELL_YES_CALLBACK,
            no_cbdata=glob.MSELL_NO_CALLBACK
        )
    )


@router.callback_query(StateFilter(MsellStates.waiting_for_confirmation), F.data.startswith(glob.MSELL_YES_CALLBACK))
async def msell_yes(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)

    # (fsm) get flow's data
    data = await state.get_data()
    if not data:
        return await callback.answer(glob.FLOW_EXPIRED, show_alert=True)

    # (core & fsm) process data
    user_id: int = data['user_id']
    quantity: int = data['quantity']
    revenue: int = data['revenue']
    single_tax: int = data['single_tax']
    msell_tax: int = data['msell_tax']

    sold_items_count_today = await service.get_sold_mc_today(user_id)

    if sold_items_count_today + quantity > glob.CHOOSE_MAT_ITEMS_LIMIT:
        await callback.message.answer(glob.MSELL_ITEMS_LIMIT_REACHED)
        await callback.answer()
        await state.clear()
        return

    member = await service.get_member(user_id)
    if member.tpay_available == 0:
        await callback.message.answer(glob.TPAY_UNAVAILABLE_ERROR)
        await callback.answer()
        await state.clear()
        return

    await service.msell(data)

    await callback.message.edit_text(f'*{glob.MSELL_YES} {(revenue - single_tax - msell_tax) / 100:.2f} tc*')
    await callback.answer()


@router.callback_query(StateFilter(MsellStates.waiting_for_confirmation), F.data.contains(glob.MSELL_NO_CALLBACK))
async def msell_no(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(glob.MSELL_NO)
    await callback.answer()
    await state.clear()
