from enum import Enum


class CommandList(str, Enum):

    # handler: empty
    # [<reply>] /command
    # /command <username:username>
    # /command <user_id:pnint>

    # handler: count
    # <reply> /command <count:any> [<description:text>]
    # /command <username:username> <count:any> [<description:text>]
    # /command <user_id:pnint> <count:any> [<description:text>]

    # # # # # # # # #
    # for creator

    # /db
    db = 'db'

    # /sql <query:text>
    sql = 'sql'

    # handler: count:pnreal
    addt = 'addt'

    # handler: count:pnreal
    delt = 'delt'

    # handler: count:real
    sett = 'sett'

    # # # # # # # # #
    # for all users

    # /help
    help = 'help'

    # /topt
    # /topt <count:nint>
    topt = 'topt'

    # handler: empty
    bal = 'bal'

    # handler: empty
    infm = 'infm'

    # handler: empty
    ttime = 'ttime'

    # handler: count:pnreal
    tpay = 'tpay'

    # <reply> /tkick [<message:text>]
    # /tkick <username:username> [<message:text>]
    # /tkick <user_id:pnint> [<message:text>]
    tkick = 'tkick'

    # <reply> /tmute <time:time> [<message:text>]
    # /tmute <username:username> <time:time> [<message:text>]
    # /tmute <user_id:pnint> <time:time> [<message:text>]
    tmute = 'tmute'

    # <reply> /tban <time:time> [<message:text>]
    # /tban <username:username> <time:time> [<message:text>]
    # /tban <user_id:pnint> <time:time> [<message:text>]
    tban = 'tban'

    # /demute
    demute = 'demute'

    # /deban
    deban = 'deban'
