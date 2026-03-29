from fastapi import APIRouter

from .endpoints import actors, films, customers, rentals, health

api_router = APIRouter()

# Include routers from different modules
api_router.include_router(health.router, tags=["health"])
api_router.include_router(actors.router, prefix="/actors", tags=["actors"])
api_router.include_router(films.router, prefix="/films", tags=["films"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(rentals.router, prefix="/rentals", tags=["rentals"])