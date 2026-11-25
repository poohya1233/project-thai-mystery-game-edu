from routers.auth import router as auth_router
from routers.game import router as game_router
from routers.player import router as player_router

__all__ = ["auth_router", "player_router", "game_router"]