from enum import Enum


class CommandList(str, Enum):
    # # # # # # # # #
    # for admin

    # /sql <query:text>
    sql = 'sql'
    # /sqls <query:text>
    sqls = 'sqls'
    # <reply> /sqlf
    sqlf = 'sqlf'
    # cog: tickets-pnreal
    addt = 'addt'
    # cog: tickets-pnreal
    delt = 'delt'
    # cog: tickets-real
    sett = 'sett'
    # cog: a1-any
    award = 'award'
    # cog: a1-any
    hire = 'hire'
    # cog: a1-any
    fire = 'fire'
    # /sched
    sched = 'sched'
    # /resetprice
    resetprice = 'resetprice'
    # /unreg
    unreg = 'unreg'
    # /db
    db = 'db'
    # /msg
    msg = 'msg'
    # cog: pure
    atxn = 'atxn'

    # # # # # # # # #
    # for all users

    # /start
    start = 'start'
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
    # cog: l-id-any
    minvo = 'minvo'
    # cog: l-id-any
    moffer = 'moffer'
    # /msell
    msell = 'msell'
    # /msend <user_id:userid>
    # /msend <user_id:userid> <description:text256>
    # /msend <username:username>
    # /msend <username:username> <description:text256>
    msend = 'msend'
    # /txn
    txn = 'txn'
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
    # /rustni
    rustni = 'rustni'
    # /p <price:pnreal>
    p = 'p'
    # /tag <user_id:userid>
    tag = 'tag'
    # /anchor
    anchor = 'anchor'
    # /reg
    reg = 'reg'
    # /cancel
    cancel = 'cancel'
