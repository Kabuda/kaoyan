# Kaoyan 11408 Study Dashboard

公网部署的 11408 二战私人学习驾驶舱，目标是支持每日规划、学习计时、学习记录和阶段复盘。

## 技术栈

- Backend: FastAPI, SQLAlchemy, MySQL, JWT
- Frontend: Vue 3, Vite, TypeScript
- Deploy: Docker Compose

## 后端本地开发

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -e .[dev]
Copy-Item ..\.env.example ..\.env
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

默认后端地址：`http://127.0.0.1:8000`

## 环境变量

复制 `.env.example` 为 `.env` 后修改：

- `DATABASE_URL`: MySQL 连接串
- `JWT_SECRET`: JWT 密钥，公网部署前必须替换
- `INITIAL_ADMIN_USERNAME`: 初始管理员用户名
- `INITIAL_ADMIN_PASSWORD`: 初始管理员密码

## 测试

```powershell
cd backend
.\.venv\Scripts\python -m pytest
```
