from enum import Enum


class CommandList(str, Enum):
    # # # # # # # # #
    # for creator

    # /sql <query:text>
    sql = 'sql'

    # cog: count-pnreal
    addt = 'addt'

    # cog: count-pnreal
    delt = 'delt'

    # cog: count-real
    sett = 'sett'

    # /sfs <message:text>
    sfs = 'sfs'

    # /db
    db = 'db'

    # # # # # # # # #
    # for all users

    #
    reg = 'reg'

    # /rusni
    rusni = 'rusni'

    # /help
    help = 'help'

    # /topt
    # /topt <count:nint>
    topt = 'topt'

    # cog: pure
    bal = 'bal'

    # cog: pure
    infm = 'infm'

    # cog: count-pnreal
    tpay = 'tpay'
