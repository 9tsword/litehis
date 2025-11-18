from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """应用配置，支持通过环境变量或 .env 文件覆盖。"""

    # 应用名称会体现在 OpenAPI 文档与日志中
    app_name: str = Field(default="LiteHIS")
    # 默认使用 SQLite，可在部署时替换为国产数据库（如 openGauss、达梦等）
    database_url: str = Field(default="sqlite:///./litehis.db")
    # 允许跨域的前端地址列表，默认指向本地 Vite 服务
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 实例化配置对象，供模块其它位置直接导入使用
settings = Settings()
