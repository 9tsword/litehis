from fastapi import APIRouter

from .appointments import router as appointments_router
from .dashboard import router as dashboard_router
from .departments import router as departments_router
from .doctors import router as doctors_router
from .patients import router as patients_router


# 统一聚合子模块路由，便于在主应用中一次性挂载
api_router = APIRouter()
api_router.include_router(dashboard_router)
api_router.include_router(departments_router)
api_router.include_router(doctors_router)
api_router.include_router(patients_router)
api_router.include_router(appointments_router)

__all__ = ["api_router"]
