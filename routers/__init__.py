from .config import Routes
from .media import router as media_router
from .auth import router as auth_router
from .docs import router as docs_router

__routes__ = Routes(routers=(docs_router, media_router, auth_router))