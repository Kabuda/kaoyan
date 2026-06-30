# Kaoyan 11408 Study Dashboard

一个面向二战考研的私人 11408 学习驾驶舱，支持每日规划、学习计时、学习记录、周复盘和目标差距追踪。当前目标基线：

- 一战成绩：政治 64、英语 46、数学 74、408 83，总分 267
- 二战目标：总分 330，数学 110，408 100，默认政治 65、英语 55
- 核心策略：数学主攻，英语不断档，408 稳步提分

## 技术栈

- Frontend: Vue 3, Vite, TypeScript, Pinia, Axios, lucide-vue-next
- Backend: FastAPI, SQLAlchemy, Alembic, MySQL, JWT
- Deploy: Docker Compose, Nginx

## 本地开发

### 后端

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -e .[dev]
Copy-Item ..\.env.example ..\.env
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

默认后端地址：`http://127.0.0.1:8000`

### 前端

```powershell
cd frontend
npm install
npm run dev
```

默认前端地址：`http://127.0.0.1:5173`

开发模式下 Vite 会把 `/api` 和 `/health` 代理到本地 FastAPI。

## Docker Compose 启动

```powershell
Copy-Item .env.example .env
docker compose up --build
```

启动后：

- Frontend: `http://127.0.0.1:8080`
- Backend: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/health`
- MySQL: `127.0.0.1:3306`

Docker 模式下前端由 Nginx 托管，并把 `/api` 反向代理到 `backend:8000`。

## 默认账号

默认管理员来自环境变量：

- `INITIAL_ADMIN_USERNAME=admin`
- `INITIAL_ADMIN_PASSWORD=change-me-now`

公网部署前必须修改 `.env` 中的 `JWT_SECRET` 和默认管理员密码。

## 环境变量

复制 `.env.example` 为 `.env` 后按需修改：

- `DATABASE_URL`: 本地后端直连 MySQL 时使用的连接串
- `MYSQL_DATABASE`: Docker Compose MySQL 数据库名
- `MYSQL_USER`: Docker Compose MySQL 用户名
- `MYSQL_PASSWORD`: Docker Compose MySQL 密码
- `MYSQL_ROOT_PASSWORD`: Docker Compose MySQL root 密码
- `MYSQL_PORT`: MySQL 暴露端口
- `BACKEND_PORT`: 后端暴露端口
- `FRONTEND_PORT`: 前端暴露端口
- `JWT_SECRET`: JWT 密钥
- `INITIAL_ADMIN_USERNAME`: 初始管理员用户名
- `INITIAL_ADMIN_PASSWORD`: 初始管理员密码
- `CORS_ORIGINS`: 允许跨域访问的前端地址
- `UPLOAD_DIR`: 题目图片上传目录
- `MAX_UPLOAD_BYTES`: 单张图片大小限制，默认 8MB
- `ARK_API_KEY`: 火山方舟 API Key；不配置时图片会保存，但 Doubao 分析会跳过
- `ARK_BASE_URL`: 火山方舟 OpenAI 兼容接口地址
- `ARK_VISION_MODEL`: Doubao 图片理解模型
- `ARK_TEXT_MODEL`: Doubao 每日复盘文本模型

## 数据库迁移

后端使用 Alembic 管理数据库结构。Docker 启动时会自动执行：

```powershell
cd backend
.\.venv\Scripts\python -m alembic upgrade head
```

## 测试与构建

后端测试：

```powershell
cd backend
.\.venv\Scripts\python -m pytest
```

前端生产构建：

```powershell
cd frontend
npm run build
```

## 公网部署建议

第一版推荐用一台云服务器部署 Docker Compose：

1. 安装 Docker 和 Docker Compose。
2. 拉取仓库并复制 `.env.example` 为 `.env`。
3. 修改 `JWT_SECRET`、数据库密码、管理员密码。
4. 执行 `docker compose up -d --build`。
5. 用服务器 Nginx、Caddy 或宝塔反向代理域名到 `127.0.0.1:${FRONTEND_PORT}`。
6. 配置 HTTPS 证书，只暴露前端入口；后端和 MySQL 不直接暴露到公网。
