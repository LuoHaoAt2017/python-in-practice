from fastapi import APIRouter, Depends

from .dependencies.auth import get_current_user
from .endpoints import actors, auth, customers, films, health, rentals

api_router = APIRouter()

# Public routes (no authentication required)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(health.router, tags=["health"])

# Protected routes (JWT authentication required)
api_router.include_router(
    actors.router, prefix="/actors", tags=["actors"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    films.router, prefix="/films", tags=["films"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    customers.router, prefix="/customers", tags=["customers"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    rentals.router, prefix="/rentals", tags=["rentals"],
    dependencies=[Depends(get_current_user)],
)
