# LiteHIS

LiteHIS 是面向中小型医院的轻量化医院信息系统（HIS）脚手架，采用 B/S 架构并兼顾信创生态兼容性。仓库包含 FastAPI + SQLModel 构建的后端服务以及 Vue 3 + Vite 打造的前端驾驶舱，可快速完成患者、医生、科室、预约等基础业务的录入与展示。

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

## 快速上手

### 1. 启动后端服务

1. 切换到 `backend/` 目录并创建虚拟环境：

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Windows 使用 .venv\\Scripts\\activate
   ```

2. 安装依赖并启动 FastAPI：

   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

   首次运行会自动在项目根目录生成 `litehis.db` SQLite 文件并完成建表。若医院上线环境要求国产数据库，可在 `backend/.env` 中覆盖 `DATABASE_URL`，或直接修改 `app/config.py` 中的默认值以连接 openGauss、PostgreSQL 等实例。

3. 访问 <http://localhost:8000/docs> 打开 Swagger UI，可直接在线调用所有 API 并查看请求/响应模型。

### 2. 启动前端驾驶舱

1. 切换到 `frontend/` 目录并准备环境：

   ```bash
   cd frontend
   cp .env.example .env    # 如需自定义后端地址请修改 VITE_API_BASE
   ```

2. 安装依赖并启动开发服务器：

   ```bash
   npm install
   npm run dev
   ```

3. 在浏览器打开 <http://localhost:5173>，即可体验驾驶舱界面。页面加载后会自动调用后端接口刷新统计卡片、列表和表单选项。

> 若遇到 npm 源无法访问，可临时执行 `npm config set registry https://registry.npmmirror.com` 切换到国内镜像，再重新安装依赖。

### 3. 日常开发小贴士

- **数据库文件**：默认位于仓库根目录，可通过删除 `litehis.db` 让系统重新初始化空表；也可以在 `.env` 中配置到持久化路径。
- **热重载**：后端使用 `uvicorn --reload`，前端 `npm run dev` 均支持热更新，无需手动重启。
- **接口联调**：可借助 Swagger UI、Postman 或 `curl` 直接调用接口；前端 Axios 客户端统一封装在 `frontend/src/api.ts`，便于扩展鉴权、请求头等逻辑。

## 示例：患者建档

以下示例演示如何通过接口完成患者建档，并在前端驾驶舱中查看结果。

### 步骤 1：调用后端接口创建患者

在终端保持后端服务运行后，另开一个终端执行：

```bash
curl -X POST "http://localhost:8000/patients/" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "张小雅",
    "gender": "female",
    "birth_date": "1996-09-12",
    "phone": "13800001234",
    "address": "广东省广州市天河区健康路 8 号"
  }'
```

接口会返回新建患者的完整信息，包括系统生成的主键与时间戳：

```json
{
  "id": 1,
  "full_name": "张小雅",
  "gender": "female",
  "birth_date": "1996-09-12",
  "phone": "13800001234",
  "id_card": null,
  "address": "广东省广州市天河区健康路 8 号",
  "created_at": "2024-03-08T06:30:41.507507",
  "updated_at": "2024-03-08T06:30:41.507511"
}
```

### 步骤 2：验证患者已入库

可以通过 `GET /patients/` 查看所有患者：

```bash
curl "http://localhost:8000/patients/"
```

或在 Swagger UI 中点击 `GET /patients/`，即可确认刚才的记录已经写入数据库。

### 步骤 3：在前端驾驶舱查看

保持前端服务运行并刷新页面，左下角的 “最新登记患者” 列表会出现 “张小雅” 的条目。若需要通过 UI 建档，只需在“登记新患者”表单填写同样的信息并点击“保存患者”，页面会弹出保存提示并自动刷新列表。

更多建档、更新、搜索的细节可在《[患者建档教程](docs/patient-registration.md)》中查看。

## 教程与延伸阅读

- [患者建档教程](docs/patient-registration.md)：一步步完成患者建档、查询、修改，以及排错建议。
- 后续可补充更多模块教程（如医生维护、门诊预约），欢迎在此目录新增文档并在此处汇总。

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

