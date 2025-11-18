# 患者建档教程

本文以“患者建档”为例，演示 LiteHIS 框架的端到端使用方式：从启动后端与前端，到调用 API、新增患者、在界面确认结果。完成本教程后，你可以轻松拓展其他业务流程，例如医生维护、门诊预约等。

## 1. 环境准备

在继续之前，请确认已按照《readme.md》中的“快速上手”步骤完成以下准备：

- 后端服务（FastAPI）在 `http://localhost:8000` 运行；
- 前端驾驶舱（Vite Dev Server）在 `http://localhost:5173` 运行；
- 本地已创建默认的 `litehis.db` 数据库文件，或者你已经配置了自定义 `DATABASE_URL`。

如果还未启动，请参考 `readme.md` 的详细说明。后续命令默认在 macOS/Linux 终端运行，Windows PowerShell 需要适度调整（如去掉 `\` 换行符）。

## 2. 通过 API 创建患者

LiteHIS 后端暴露 RESTful 接口，患者建档的入口为 `POST /patients/`。可以使用 `curl`、HTTPie 或 Swagger UI 进行调试。

### 2.1 使用 curl 发起请求

```bash
curl -X POST "http://localhost:8000/patients/" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "张小雅",
    "gender": "female",
    "birth_date": "1996-09-12",
    "phone": "13800001234",
    "id_card": "441900199609120321",
    "address": "广东省广州市天河区健康路 8 号"
  }'
```

请求体字段说明：

| 字段 | 说明 | 是否必填 |
| ---- | ---- | -------- |
| `full_name` | 患者姓名 | ✅ |
| `gender` | 性别，可选 `female`、`male`、`other`、`unknown` | ✅ |
| `birth_date` | 出生日期（YYYY-MM-DD） | 可选 |
| `phone` | 联系电话 | 可选 |
| `id_card` | 身份证或就诊卡号 | 可选 |
| `address` | 常住地址 | 可选 |

响应示例：

```json
{
  "id": 1,
  "full_name": "张小雅",
  "gender": "female",
  "birth_date": "1996-09-12",
  "phone": "13800001234",
  "id_card": "441900199609120321",
  "address": "广东省广州市天河区健康路 8 号",
  "created_at": "2024-03-08T06:30:41.507507",
  "updated_at": "2024-03-08T06:30:41.507511"
}
```

### 2.2 查看患者列表

```bash
curl "http://localhost:8000/patients/"
```

返回值为按创建时间倒序排列的患者数组。若需要根据编号定位特定患者，也可调用 `GET /patients/{id}`：

```bash
curl "http://localhost:8000/patients/1"
```

### 2.3 修改患者信息（可选）

接口 `PATCH /patients/{id}` 支持局部字段更新，例如补充地址：

```bash
curl -X PATCH "http://localhost:8000/patients/1" \
  -H "Content-Type: application/json" \
  -d '{ "address": "广州市天河区住院部 5F" }'
```

## 3. 在前端驾驶舱完成患者建档

前端的“登记新患者”卡片与后端接口保持一致，表单字段会自动转换成所需的 JSON。操作流程：

1. 打开 <http://localhost:5173>；
2. 在 “登记新患者” 卡片内填写姓名、性别、出生日期、联系电话等信息；
3. 点击“保存患者”，页面会调用 `POST /patients/` 接口；
4. 保存成功后，卡片下方会以通知提示，右下角的“最新登记患者”列表自动刷新。

如果需要在移动设备或平板上测试，只需确保能访问运行前端的主机，并在 `.env` 中将 `VITE_API_BASE` 指向后端真实地址。

## 4. 数据校验与排错建议

- **查看数据库原始数据**：默认 SQLite 数据文件位于项目根目录，可用 `sqlite3 litehis.db` 或 TablePlus 等工具查看 `patient` 表。
- **跨域/端口问题**：若前端运行在非默认端口，请在 `backend/.env` 中设置 `CORS_ORIGINS=["http://your-host:port"]` 并重启后端。
- **常见 HTTP 错误**：
  - `422 Unprocessable Entity`：请求体字段缺失或格式不正确，请参考上方字段说明。
  - `404 Not Found`：访问了不存在的患者编号，请确认 ID 或重新创建数据。
- **批量导入建议**：可编写脚本读取 Excel/CSV，通过调用 `POST /patients/` 批量导入；若需要更高性能，可扩展批量插入接口或引入异步任务队列。

## 5. 下一步

完成患者建档后，可继续探索以下能力：

- 调用 `POST /departments/`、`POST /doctors/` 维护科室与医生档案；
- 在前端“安排门诊预约”卡片中选择患者和医生，创建 `POST /appointments/` 记录；
- 基于现有模型扩展字段，例如增加患者既往史、联系方式标签等。

欢迎根据医院实际流程自定义字段和界面，LiteHIS 的代码结构与配置都已为二次开发准备就绪。
