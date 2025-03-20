from typing import Type

from comparser.overload import CommandOverloadGroup, CommandOverload
from comparser.types.arg_type import Text256, Username, UserID, CommandArgumentType


# pure cog
# <reply> /command
# /command
# /command <username:username>
# /command <user_id:pnint>
def pure() -> CommandOverloadGroup:
    return CommandOverloadGroup([
        CommandOverload(reply_required=True),
        CommandOverload(),
        CommandOverload().add('username', Username),
        CommandOverload().add('user_id', UserID)
    ])


# count cog
# <creator> <reply> /command <tickets:xreal>
# <creator> <reply> /command <tickets:xreal> <description:text256>
# <creator> /command <username:username> <tickets:xreal>
# <creator> /command <username:username> <tickets:xreal> <description:text256>
# <creator> /command <user_id:userid> <tickets:xreal>
# <creator> /command <user_id:userid> <tickets:xreal> <description:text256>
def tickets(arg_type: Type[CommandArgumentType]) -> CommandOverloadGroup:
    return CommandOverloadGroup([
        CommandOverload(reply_required=True, no_self_reply_required=True)
        .add('tickets', arg_type),

        CommandOverload(reply_required=True, no_self_reply_required=True)
        .add('tickets', arg_type)
        .add('description', Text256),

        CommandOverload()
        .add('username', Username)
        .add('tickets', arg_type),

        CommandOverload()
        .add('username', Username)
        .add('tickets', arg_type)
        .add('description', Text256),

        CommandOverload()
        .add('user_id', UserID)
        .add('tickets', arg_type),

        CommandOverload()
        .add('user_id', UserID)
        .add('tickets', arg_type)
        .add('description', Text256)
    ], creator_required=True)
