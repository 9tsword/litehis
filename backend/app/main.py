from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .config import settings
from .database import init_db


def create_application() -> FastAPI:
    """应用工厂函数，供测试与实际部署复用。"""

    # 以配置中的标题初始化 FastAPI 实例，便于前端或文档展示
    app = FastAPI(title=settings.app_name)

    # 配置 CORS，确保前端开发和多端访问时接口可被跨域调用
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup() -> None:
        """服务启动时自动建表，避免首次运行报错。"""

        init_db()

    @app.get("/health", tags=["health"])
    def healthcheck() -> dict[str, str]:
        """提供简单的健康检查，用于探活或监控。"""

        return {"status": "ok"}

    # 汇总注册所有子路由，保证模块化接口能被访问
    app.include_router(api_router)

    return app


# 默认导出供 ASGI 服务器（如 uvicorn、gunicorn）直接加载
app = create_application()
