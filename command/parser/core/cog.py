from typing import Type

from command.parser.core.overload import CommandOverloadGroup, CommandOverload
from model.types.custom.flags import AdminFlag
from model.types.custom.primitives import xreal, TicketonomicsType, Text256, Username, UserID
from resources.glob import TICKETS_ARG, DESCRIPTION_ARG, USERNAME_ARG, USER_ID_ARG


# [<admin>] <reply> /command
# [<admin>] /command
# [<admin>] /command <username:username>
# [<admin>] /command <user_id:pnint>
def pure(creator_required: bool = False, private_required: bool = False) -> CommandOverloadGroup:
    return CommandOverloadGroup(
        [
            CommandOverload(reply=True),
            CommandOverload(),
            CommandOverload().add(USERNAME_ARG, Username),
            CommandOverload().add(USER_ID_ARG, UserID)
        ],
        admin=creator_required,
        private=private_required
    )


# <admin> <reply> /command <tickets:xreal>
# <admin> <reply> /command <tickets:xreal> <description:text256>
# <admin> /command <username:username> <tickets:xreal>
# <admin> /command <username:username> <tickets:xreal> <description:text256>
# <admin> /command <user_id:userid> <tickets:xreal>
# <admin> /command <user_id:userid> <tickets:xreal> <description:text256>
def tickets(arg_type: Type[TicketonomicsType], admin_required: bool) -> CommandOverloadGroup:
    if not xreal(arg_type):
        raise ValueError()

    return a1d_any(
        a1_name=TICKETS_ARG,
        a1_type=arg_type,
        admin_required=admin_required,
        no_self_reply_required=True
    )


# <admin> <reply> /command <a1:any>
# <admin> /command <username:username> <a1:any>
# <admin> /command <user_id:userid> <a1:any>
def a1_any(a1_name: str, a1_type: Type[TicketonomicsType], admin_required: bool,
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
    ], admin=admin_required)


# <admin> <reply> /command <a1:any>
# <admin> <reply> /command <a1:any> <description:text256>
# <admin> /command <username:username> <a1:any>
# <admin> /command <username:username> <a1:any> <description:text256>
# <admin> /command <user_id:userid> <a1:any>
# <admin> /command <user_id:userid> <a1:any> <description:text256>
def a1d_any(a1_name: str, a1_type: Type[TicketonomicsType], admin_required: bool,
            no_self_reply_required: bool = False) -> CommandOverloadGroup:
    return CommandOverloadGroup([
        CommandOverload(reply=True, no_self_reply=no_self_reply_required)
        .add(a1_name, a1_type),

        CommandOverload(reply=True, no_self_reply=no_self_reply_required)
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
    ], admin=admin_required)


#yl /command
#ye /command <id_name:id_type>
#sl <admin> <reply> /command -a
#sl <admin> /command -a <username:username>
#sl <admin> /command -a <user_id:userid>
#se <admin> /command -a <id_name:id_type>
def le_id_any(id_name: str, id_type: Type[TicketonomicsType]) -> CommandOverloadGroup:
    l = 'list'
    e = 'element'
    return CommandOverloadGroup([
        CommandOverload(otype=l),

        CommandOverload(otype=e)
        .add(id_name, id_type),

        CommandOverload(otype=l, reply=True, admin=True)
        .flag(AdminFlag),

        CommandOverload(otype=l, admin=True)
        .flag(AdminFlag)
        .add(USERNAME_ARG, Username),

        CommandOverload(otype=l, admin=True)
        .flag(AdminFlag)
        .add(USER_ID_ARG, UserID),

        CommandOverload(otype=e, admin=True)
        .flag(AdminFlag)
        .add(id_name, id_type)
    ])
