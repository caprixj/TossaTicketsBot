from enum import Enum


class CommandList(str, Enum):
    # # # # # # # # #
    # for creator

    # /sql <query:text>
    sql = 'sql'

    # cog: tickets-pnreal
    addt = 'addt'

    # cog: tickets-pnreal
    delt = 'delt'

    # cog: tickets-real
    sett = 'sett'

    # /sfs <page_message:text>
    sfs = 'sfs'

    # /db
    db = 'db'

    # cog: a1_any
    award = 'award'

    # cog: pure
    xltrans = 'xltrans'

    # # # # # # # # #
    # for all users

    #
    reg = 'reg'

    # /rusni
    rusni = 'rusni'

    # /help
    help = 'help'

    # /ltrans
    ltrans = 'ltrans'

    # /laward
    laward = 'laward'

    # /topt
    # /topt <count:nint>
    topt = 'topt'

    # cog: pure
    bal = 'bal'

    # cog: pure
    infm = 'infm'

    # cog: tickets-pnreal
    tpay = 'tpay'
