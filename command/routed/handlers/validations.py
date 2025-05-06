from aiogram.types import User, Message, CallbackQuery

from resources.const import glob
from service import service_core as service


async def validate_message(message: Message) -> bool:
    user_is_member = await validate_user(message.from_user)

    if not user_is_member:
        await message.reply(glob.NOT_MEMBER_ERROR)

    if message.reply_to_message is not None:
        reply_user_is_member = await validate_user(message.reply_to_message.from_user)

        if not reply_user_is_member:
            await message.reply(glob.TARGET_NOT_MEMBER_ERROR)

        return user_is_member and reply_user_is_member

    return user_is_member


async def validate_user(user: User) -> bool:
    member = await service.get_member(user.id)
    member_exists = member is not None

    if member_exists:
        await service.update_member(user, member)

    return member_exists


async def validate_callback(callback: CallbackQuery) -> bool:
    user_is_member = await validate_user(callback.from_user)

    if not user_is_member:
        await callback.answer(glob.NOT_MEMBER_ERROR, show_alert=True)

    return user_is_member
