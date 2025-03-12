from comparser.Overload import Overload
from comparser.enums.OverloadType import OverloadType
from comparser.enums.ParamType import ParamType as pt

COUNT = 'count'
DESCRIPTION = 'description'
USERNAME = 'username'
USER_ID = 'user_id'

QUERY = 'query'
SIZE = 'size'


# {<creator>} {<reply>} /command
async def reply_empty(name: str = None, creator_filter: bool = False, reply_optional: bool = False) -> Overload:
    return Overload(
        name=name,
        type_=OverloadType.reply,
        creator_filter=creator_filter,
        reply_filter=True,
        reply_optional=reply_optional
    )


# {<creator>} /command <username:username>
async def username_empty(name: str = None, creator_filter: bool = False) -> Overload:
    return (Overload(
        type_=OverloadType.username,
        creator_filter=creator_filter,
        name=name)
            .add_param(USERNAME, pt.username))


# {<creator>} /command <user_id:pzint>
async def user_id_empty(name: str = None, creator_filter: bool = False) -> Overload:
    return (Overload(
        type_=OverloadType.user_id,
        creator_filter=creator_filter,
        name=name)
            .add_param(USER_ID, pt.pzint))


# {<creator>} <reply> /command <count:pzint> [<description:text>]
async def reply_count(count_type: pt, name: str = None, creator_filter: bool = False) -> Overload:
    return ((await reply_empty(name, creator_filter))
            .add_param(COUNT, count_type)
            .add_param(DESCRIPTION, pt.text, optional=True))


# {<creator>} /command <username:username> <count:pzint> [<description:text>]
async def username_count(count_type: pt, name: str = None, creator_filter: bool = False) -> Overload:
    return ((await username_empty(name, creator_filter))
            .add_param(COUNT, count_type)
            .add_param(DESCRIPTION, pt.text, optional=True))


# {<creator>} /command <user_id:pzint> <count:pzint> [<description:text>]
async def user_id_count(count_type: pt, name: str = None, creator_filter: bool = False) -> Overload:
    return ((await user_id_empty(name, creator_filter))
            .add_param(COUNT, count_type)
            .add_param(DESCRIPTION, pt.text, optional=True))
