from .a_txn import router as a_txn
from .bal import router as bal
from .infm import router as infm
from .tpool import router as tpool

info_routers = [a_txn, bal, infm, tpool]
