from enum import Enum


class CommandList(str, Enum):

    # handler: empty
    # [<reply>] /command
    # /command <username:username>
    # /command <user_id:pzint>

    # handler: count
    # <reply> /command <count:any> [<description:text>]
    # /command <username:username> <count:any> [<description:text>]
    # /command <user_id:pzint> <count:any> [<description:text>]

    # # # # # # # # #
    # for creator

    # /db
    db = 'db'

    # /sql <query:text>
    sql = 'sql'

    # handler: count:pzint
    addt = 'addt'

    # handler: count:pzint
    delt = 'delt'

    # handler: count:int
    sett = 'sett'

    # # # # # # # # #
    # for all users

    # /help
    help = 'help'

    # /topt
    # /topt <count:zint>
    topt = 'topt'

    # handler: empty
    bal = 'bal'

    # handler: empty
    infm = 'infm'

    # handler: empty
    ttime = 'ttime'

    # handler: count:pzint
    tpay = 'tpay'

    # <reply> /tkick [<message:text>]
    # /tkick <username:username> [<message:text>]
    # /tkick <user_id:pzint> [<message:text>]
    tkick = 'tkick'

    # <reply> /tmute <time:time> [<message:text>]
    # /tmute <username:username> <time:time> [<message:text>]
    # /tmute <user_id:pzint> <time:time> [<message:text>]
    tmute = 'tmute'

    # <reply> /tban <time:time> [<message:text>]
    # /tban <username:username> <time:time> [<message:text>]
    # /tban <user_id:pzint> <time:time> [<message:text>]
    tban = 'tban'

    # /demute
    demute = 'demute'

    # /deban
    deban = 'deban'
