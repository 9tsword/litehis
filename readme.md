# LiteHIS

LiteHIS 是面向国内医院的轻量化医院信息系统（HIS）脚手架，采用 B/S 架构并兼顾信创生态兼容性。仓库包含 FastAPI + SQLModel 构建的后端服务以及 Vue 3 + Vite 打造的前端驾驶舱，可快速完成患者、医生、科室、预约等基础业务的录入与展示。

## 架构总览

```
┌──────────┐      RESTful API      ┌──────────────┐
│  Vue 3   │  <----------------->  │   FastAPI    │
│  Vite    │                       │  SQLModel    │
└──────────┘                       └──────────────┘
      │                                   │
      │                                   ├── SQLite（默认，可替换 openGauss、PostgreSQL 等）
      │                                   └── Redis / MQ 等可按需扩展
```

- **后端**：FastAPI 提供患者、医生、科室、预约、仪表盘等模块化接口，SQLModel 映射数据库实体，默认使用 SQLite，可替换为国产数据库。
- **前端**：Vue 3 + TypeScript + Vite 构建的单页应用，内置轻量化 UI，提供四大表单与概览面板，支持自定义 API 基地址。

## 本地开发

### 准备环境

- Python ≥ 3.10
- Node.js ≥ 18（前端构建）

### 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows 使用 .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

后端默认生成 `litehis.db` SQLite 文件，首次启动会自动建表。

### 启动前端

```bash
cd frontend
cp .env.example .env    # 如需自定义后端地址请修改 VITE_API_BASE
npm install
npm run dev
```

浏览器访问 <http://localhost:5173>，即可体验驾驶舱界面并与后端交互。

## 目录结构

```
backend/
  app/
    api/           # FastAPI 路由（患者、医生、科室、预约、仪表盘）
    config.py      # 应用配置
    database.py    # 数据库初始化及会话依赖
    main.py        # FastAPI 入口
    models.py      # SQLModel 数据实体与 Pydantic 模型
  requirements.txt
frontend/
  src/
    components/    # Vue 复用组件
    api.ts         # Axios 封装
    App.vue        # 主界面
    main.ts        # 应用入口
    style.css      # 全局样式
  package.json
  vite.config.ts
  tsconfig*.json
.gitignore
readme.md
```

## 下一步建议

- 引入统一身份认证、RBAC 与操作审计。
- 扩展药房、收费、检验等模块，打通第三方系统接口（医保、LIS、PACS）。
- 增加自动化测试与 CI/CD，纳入性能压测脚本。

