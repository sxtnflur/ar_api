from routers.config import Routes
from routers.media import router as media_router
from routers.auth import router as auth_router

__routes__ = Routes(routers=(media_router, auth_router))