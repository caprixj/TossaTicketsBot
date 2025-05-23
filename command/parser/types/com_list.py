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
    # cog: a1_any
    award = 'award'
    # cog: a1_any
    hire = 'hire'
    # cog: a1_any
    fire = 'fire'
    # /sched
    sched = 'sched'
    # /resetprice
    resetprice = 'resetprice'
    # /unreg
    unreg = 'unreg'

    # cog: pure
    xltrans = 'xltrans'

    # # # # # # # # #
    # for all users

    # /help
    help = 'help'
    # cog: pure
    infm = 'infm'
    # cog: pure
    bal = 'bal'
    # cog: pure
    balm = 'balm'
    # /tbox
    tbox = 'tbox'
    # cog: tickets-pnreal
    tpay = 'tpay'
    # /mbuy
    mbuy = 'mbuy'
    # /msell
    msell = 'msell'
    # /ltrans
    ltrans = 'ltrans'
    # cog: pure
    laward = 'laward'
    # /topt
    # /topt <count:nint>
    # /topt %
    # /topt % <count:nint>
    topt = 'topt'
    # /topm
    # /topm <count:nint>
    # /topm %
    # /topm % <count:nint>
    topm = 'topm'
    # /tpool
    tpool = 'tpool'
    # /rates
    rates = 'rates'
    # /alert
    alert = 'alert'
    # /unalert
    unalert = 'unalert'
    # /rusni
    rusni = 'rusni'
    # /p <price:pnreal>
    p = 'p'
    # /tag
    tag = 'tag'
    # /anchor
    anchor = 'anchor'
    # /reg
    reg = 'reg'
