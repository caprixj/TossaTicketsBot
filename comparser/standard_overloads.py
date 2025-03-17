from comparser.overload import Overload
from comparser.enums.overload_type import OverloadType
from comparser.enums.param_type import ParamType as pt

COUNT = 'count'
DESCRIPTION = 'description'
USERNAME = 'username'
USER_ID = 'user_id'

QUERY = 'query'
SIZE = 'size'


# {<creator>} {<reply>} /command
async def reply_empty(
        name: str = None,
        creator_filter: bool = False,
        reply_optional: bool = False,
        self_reply_filter: bool = False) -> Overload:
    return Overload(
        name=name,
        type_=OverloadType.reply,
        creator_filter=creator_filter,
        reply_filter=True,
        self_reply_filter=self_reply_filter,
        reply_optional=reply_optional
    )


# {<creator>} /command <username:username>
async def username_empty(name: str = None, creator_filter: bool = False) -> Overload:
    return (Overload(
        type_=OverloadType.username,
        creator_filter=creator_filter,
        name=name)
            .add_param(USERNAME, pt.username))


# {<creator>} /command <user_id:pnint>
async def user_id_empty(name: str = None, creator_filter: bool = False) -> Overload:
    return (Overload(
        type_=OverloadType.user_id,
        creator_filter=creator_filter,
        name=name)
            .add_param(USER_ID, pt.pnint))


# {<creator>} <reply> /command <count:pnint> [<description:text>]
async def reply_count(
        count_type: pt,
        name: str = None,
        creator_filter: bool = False,
        self_reply_filter: bool = False) -> Overload:
    return ((await reply_empty(
        name=name,
        creator_filter=creator_filter,
        self_reply_filter=self_reply_filter))
            .add_param(COUNT, count_type)
            .add_param(DESCRIPTION, pt.text, optional=True))


# {<creator>} /command <username:username> <count:pnint> [<description:text>]
async def username_count(count_type: pt, name: str = None, creator_filter: bool = False) -> Overload:
    return ((await username_empty(name, creator_filter))
            .add_param(COUNT, count_type)
            .add_param(DESCRIPTION, pt.text, optional=True))


# {<creator>} /command <user_id:pnint> <count:pnint> [<description:text>]
async def user_id_count(count_type: pt, name: str = None, creator_filter: bool = False) -> Overload:
    return ((await user_id_empty(name, creator_filter))
            .add_param(COUNT, count_type)
            .add_param(DESCRIPTION, pt.text, optional=True))
