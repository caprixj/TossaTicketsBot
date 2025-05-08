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
    # cog: a1_any
    hire = 'hire'
    # cog: a1_any
    fire = 'fire'
    # /resetprice
    resetprice = 'resetprice'
    # /unreg
    unreg = 'unreg'

    # # # # # # # # #
    # for all users

    # /help
    help = 'help'
    # cog: pure
    infm = 'infm'
    # cog: pure
    bal = 'bal'
    # /tbox
    tbox = 'tbox'
    # cog: tickets-pnreal
    tpay = 'tpay'
    # cog: pure
    ltrans = 'ltrans'
    # cog: pure
    laward = 'laward'
    # /topt
    # /topt <count:nint>
    # /topt %
    # /topt % <count:nint>
    topt = 'topt'
    # /tpool
    tpool = 'tpool'
    # /alert
    alert = 'alert'
    # /unalert
    unalert = 'unalert'
    # /rusni
    rusni = 'rusni'
    # /p <price:pnreal>
    p = 'p'
    # /reg
    reg = 'reg'
