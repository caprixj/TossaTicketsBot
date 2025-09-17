from .balm import router as balm
from .minvo import router as minvo
from .moffer import router as moffer
from .msell import router as msell
from .msend import router as msend
from .rates import router as rates
from .tbox import router as tbox

mat_trading_routers = [balm, minvo, moffer, msell, msend, rates, tbox]
