from .handlers import handlers_routers
from .callbacks import callbacks_routers
from .util.catch_all_router import router as catch_all_router

# (!) the order of the elements in the list might be crucial
all_routers = [*handlers_routers, *callbacks_routers, catch_all_router]
