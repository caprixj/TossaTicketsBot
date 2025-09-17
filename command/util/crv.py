import random

from aiogram.types import Message

from command.parser.results import CommandParserResult
from resources import glob
from resources.rands import crv_messages


async def reply_by_crv(message: Message, cpr: CommandParserResult):
    out = get_random_crv_message() \
        if cpr.creator_violation else glob.COM_PARSER_FAILED

    await message.reply(out)


def get_random_crv_message() -> str:
    return crv_messages[random.randint(0, len(crv_messages) - 1)]
