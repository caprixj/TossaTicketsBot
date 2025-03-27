from aiogram.types import User, Message

from resources.const import glob
from service.service_core import Service


async def validate_message(service: Service, message: Message) -> bool:
    user_is_member = await validate_user(service, message.from_user)

    if not user_is_member:
        await message.reply(glob.NOT_MEMBER_ERROR)

    if message.reply_to_message is not None:
        reply_user_is_member = await validate_user(service, message.reply_to_message.from_user)

        if not reply_user_is_member:
            await message.reply(glob.TARGET_NOT_MEMBER_ERROR)

        return user_is_member and reply_user_is_member

    return user_is_member


async def validate_user(service: Service, user: User) -> bool:
    member = await service.get_member(user.id)
    member_exists = member is not None

    if member_exists:
        await service.update_member(user, member)

    return member_exists
