from typing import Type

from command.parser.core.overload import CommandOverloadGroup, CommandOverload
from model.types.ticketonomics_types import xreal, TicketonomicsType, Text256, Username, UserID
from resources.const.glob import TICKETS_ARG, DESCRIPTION_ARG, USERNAME_ARG, USER_ID_ARG


# [<creator>] <reply> /command
# [<creator>] /command
# [<creator>] /command <username:username>
# [<creator>] /command <user_id:pnint>
def pure(creator_required: bool = False) -> CommandOverloadGroup:
    return CommandOverloadGroup([
        CommandOverload(reply=True),
        CommandOverload(),
        CommandOverload().add(USERNAME_ARG, Username),
        CommandOverload().add(USER_ID_ARG, UserID)
    ], creator=creator_required)


# <creator> <reply> /command <tickets:xreal>
# <creator> <reply> /command <tickets:xreal> <description:text256>
# <creator> /command <username:username> <tickets:xreal>
# <creator> /command <username:username> <tickets:xreal> <description:text256>
# <creator> /command <user_id:userid> <tickets:xreal>
# <creator> /command <user_id:userid> <tickets:xreal> <description:text256>
def tickets(arg_type: Type[TicketonomicsType], creator_required: bool) -> CommandOverloadGroup:
    if not xreal(arg_type):
        raise ValueError()

    return a1d_any(
        a1_name=TICKETS_ARG,
        a1_type=arg_type,
        creator_required=creator_required,
        no_self_reply_required=True
    )


# <creator> <reply> /command <a1:any>
# <creator> /command <username:username> <a1:any>
# <creator> /command <user_id:userid> <a1:any>
def a1_any(a1_name: str, a1_type: Type[TicketonomicsType], creator_required: bool,
           no_self_reply_required: bool = False) -> CommandOverloadGroup:
    return CommandOverloadGroup([
        CommandOverload(
            reply=True,
            no_self_reply=no_self_reply_required)
        .add(a1_name, a1_type),

        CommandOverload()
        .add(USERNAME_ARG, Username)
        .add(a1_name, a1_type),

        CommandOverload()
        .add(USER_ID_ARG, UserID)
        .add(a1_name, a1_type)
    ], creator=creator_required)


# <creator> <reply> /command <a1:any>
# <creator> <reply> /command <a1:any> <description:text256>
# <creator> /command <username:username> <a1:any>
# <creator> /command <username:username> <a1:any> <description:text256>
# <creator> /command <user_id:userid> <a1:any>
# <creator> /command <user_id:userid> <a1:any> <description:text256>
def a1d_any(a1_name: str, a1_type: Type[TicketonomicsType], creator_required: bool,
            no_self_reply_required: bool = False) -> CommandOverloadGroup:
    return CommandOverloadGroup([
        CommandOverload(
            reply=True,
            no_self_reply=no_self_reply_required)
        .add(a1_name, a1_type),

        CommandOverload(
            reply=True,
            no_self_reply=no_self_reply_required)
        .add(a1_name, a1_type)
        .add(DESCRIPTION_ARG, Text256),

        CommandOverload()
        .add(USERNAME_ARG, Username)
        .add(a1_name, a1_type),

        CommandOverload()
        .add(USERNAME_ARG, Username)
        .add(a1_name, a1_type)
        .add(DESCRIPTION_ARG, Text256),

        CommandOverload()
        .add(USER_ID_ARG, UserID)
        .add(a1_name, a1_type),

        CommandOverload()
        .add(USER_ID_ARG, UserID)
        .add(a1_name, a1_type)
        .add(DESCRIPTION_ARG, Text256)
    ], creator=creator_required)
