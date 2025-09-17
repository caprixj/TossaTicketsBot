from .alert import alerts_routers
from .award import award_routers
from .database import database_routers
from .fun import fun_routers
from .helper import helper_routers
from .info import info_routers
from .job import job_routers
from .mat import mat_trading_routers
from .other import other_routers
from .reg import reg_routers
from .ticket import ticket_routers
from .top import top_routers
from .update import update_routers

handlers_routers = [
    *alerts_routers,
    *award_routers,
    *database_routers,
    *fun_routers,
    *helper_routers,
    *info_routers,
    *job_routers,
    *mat_trading_routers,
    *other_routers,
    *reg_routers,
    *ticket_routers,
    *top_routers,
    *update_routers
]
