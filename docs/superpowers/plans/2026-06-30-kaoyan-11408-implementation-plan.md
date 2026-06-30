# 11408 二战私人学习驾驶舱实现计划

## 前置说明

设计文档已确认：`docs/superpowers/specs/2026-06-30-kaoyan-11408-design.md`。

本机未安装 `writing-plans` 技能，因此本文件按设计文档手动拆解实现计划。计划目标是把项目从空仓库推进到可本地运行、可 Docker Compose 启动、具备核心学习闭环的 Vue + FastAPI 应用。

## 总体顺序

1. 搭建仓库基础结构。
2. 实现后端基础设施和认证。
3. 实现后端学习业务 API。
4. 实现前端项目、路由、登录和布局。
5. 实现每日规划、计时、记录、统计、复盘页面。
6. 接入 Docker Compose。
7. 补充测试、README 和本地验证。

## 阶段 1：仓库和项目骨架

目标：建立可开发的前后端目录，先让工具链能跑起来。

任务：

- 创建 `backend/`。
- 创建 `frontend/`。
- 创建根目录 `.gitignore`。
- 创建根目录 `.env.example`。
- 更新 `README.md`，写明项目定位、技术栈、启动方式占位。
- 初始化后端依赖文件。
- 初始化前端 Vite Vue TypeScript 项目。

后端建议文件：

- `backend/pyproject.toml`
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/core/database.py`
- `backend/app/api/__init__.py`

前端建议文件：

- `frontend/package.json`
- `frontend/index.html`
- `frontend/vite.config.ts`
- `frontend/src/main.ts`
- `frontend/src/App.vue`
- `frontend/src/router/index.ts`

验收：

- 后端可以运行 `uvicorn app.main:app --reload`。
- 前端可以运行 `npm run dev`。
- 根目录无不必要的缓存文件进入 git。

## 阶段 2：后端认证与数据库基础

目标：公网部署前提下先完成登录保护、数据库连接和初始管理员。

任务：

- 配置环境变量读取。
- 配置 PostgreSQL 数据库连接。
- 配置 SQLAlchemy session。
- 定义 `User` 模型。
- 实现密码哈希和校验。
- 实现 JWT 创建和解析。
- 实现启动时创建初始管理员。
- 实现认证依赖 `get_current_user`。
- 实现认证接口。

接口：

- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/change-password`
- `GET /health`

验收：

- 未登录访问受保护接口返回 401。
- 使用 `.env` 里的管理员账号可以登录。
- 登录后可以访问 `/api/auth/me`。
- 密码不明文存储。

## 阶段 3：备考档案 API

目标：保存用户的一战基线和二战目标。

任务：

- 定义 `ExamProfile` 模型。
- 首次访问时自动创建默认档案。
- 默认写入一战成绩和目标分。
- 支持更新档案。

接口：

- `GET /api/profile`
- `PUT /api/profile`

默认值：

- 一战政治：64
- 一战英语：46
- 一战数学：74
- 一战 408：83
- 目标政治：65
- 目标英语：55
- 目标数学：110
- 目标 408：100
- 目标总分：330

验收：

- 登录后能获取默认档案。
- 修改目标分和每日目标分钟数后能持久化。

## 阶段 4：每日任务 API

目标：实现每日规划的后端主模型和状态流转。

任务：

- 定义 `StudyTask` 模型。
- 定义科目、模块、任务类型、任务状态枚举。
- 实现任务 CRUD。
- 实现完成、跳过、延期。
- 实现今日基础计划生成。
- 限制所有任务只能访问当前用户的数据。

接口：

- `GET /api/tasks?date=YYYY-MM-DD`
- `POST /api/tasks`
- `PUT /api/tasks/{task_id}`
- `DELETE /api/tasks/{task_id}`
- `POST /api/tasks/{task_id}/complete`
- `POST /api/tasks/{task_id}/skip`
- `POST /api/tasks/{task_id}/postpone`
- `POST /api/tasks/generate-daily-template`

验收：

- 可以创建今日任务。
- 可以按日期获取任务。
- 状态流转正确。
- 一键生成计划包含英语、数学、408、政治任务。

## 阶段 5：计时与学习记录 API

目标：实现任务计时和记录沉淀。

任务：

- 定义 `TimerSession` 模型。
- 定义 `StudyRecord` 模型。
- 实现当前运行中计时查询。
- 实现开始、暂停、继续、结束。
- 后端限制同一时间只有一个运行中计时。
- 结束计时时生成学习记录。
- 支持手动补录学习记录。
- 结束计时后回写任务实际分钟数。

接口：

- `GET /api/timer/current`
- `POST /api/timer/start`
- `POST /api/timer/pause`
- `POST /api/timer/resume`
- `POST /api/timer/finish`
- `GET /api/records`
- `POST /api/records`
- `PUT /api/records/{record_id}`
- `DELETE /api/records/{record_id}`

验收：

- 从任务开始计时后，任务进入进行中。
- 有运行中计时时，再开始另一个计时返回 409。
- 暂停和继续会保留累计时间。
- 结束计时后生成记录。
- 记录列表能按日期和科目筛选。

## 阶段 6：统计与周复盘 API

目标：为仪表盘和复盘页提供聚合数据。

任务：

- 实现仪表盘统计服务。
- 实现日期范围统计服务。
- 实现各科分布统计。
- 定义 `WeeklyReview` 模型。
- 实现周复盘 CRUD。

接口：

- `GET /api/stats/dashboard`
- `GET /api/stats/range`
- `GET /api/stats/subject-distribution`
- `GET /api/reviews/weekly`
- `POST /api/reviews/weekly`
- `PUT /api/reviews/weekly/{review_id}`
- `DELETE /api/reviews/weekly/{review_id}`

统计内容：

- 今日总分钟数
- 今日目标完成率
- 本周总分钟数
- 本月总分钟数
- 各科投入占比
- 计划完成率
- 最近 7 天趋势
- 英语连续学习天数
- 数学周投入占比
- 408 周投入占比

验收：

- 首页可以拿到一组完整统计数据。
- 没有记录时统计接口返回 0 和空数组，不报错。
- 周复盘可以创建、编辑、查看。

## 阶段 7：前端基础与登录

目标：建立前端应用框架、登录态和基础布局。

任务：

- 初始化 Vue 3 + Vite + TypeScript。
- 配置 Vue Router。
- 配置 Pinia。
- 配置 Axios API 客户端。
- 实现 token 存储和 401 处理。
- 实现登录页。
- 实现登录态路由守卫。
- 实现主布局和导航。

页面：

- `LoginView.vue`
- `DashboardView.vue`
- `PlansView.vue`
- `TimerView.vue`
- `RecordsView.vue`
- `ReviewView.vue`
- `SettingsView.vue`

验收：

- 未登录访问业务页跳转登录页。
- 登录成功后进入仪表盘。
- 刷新页面后登录态仍可恢复。
- 退出登录后 token 被清理。

## 阶段 8：前端核心页面

目标：完成用户每天真正会使用的学习闭环。

任务：

- 实现仪表盘。
- 实现每日规划页。
- 实现任务表单。
- 实现一键生成今日计划。
- 实现计时页和运行中计时组件。
- 实现记录列表和手动补录。
- 实现统计复盘页图表。
- 实现周复盘表单。
- 实现设置页。

页面验收：

- 仪表盘显示今日任务、今日时长、目标完成率、弱项提醒和 7 天趋势。
- 计划页能创建、编辑、完成、跳过、延期任务。
- 计时页能开始、暂停、继续、结束任务计时。
- 记录页能筛选和补录记录。
- 复盘页能看到统计图表并填写周复盘。
- 设置页能编辑备考档案和目标分。

## 阶段 9：Docker Compose 与部署基础

目标：让项目具备公网部署前的标准启动方式。

任务：

- 创建 `backend/Dockerfile`。
- 创建 `frontend/Dockerfile`。
- 创建根目录 `docker-compose.yml`。
- 配置 postgres volume。
- 配置后端环境变量。
- 配置前端构建产物服务。
- 补充 `.env.example`。

服务：

- `postgres`
- `backend`
- `frontend`

验收：

- `docker compose up --build` 可以启动完整系统。
- 前端能访问后端。
- 后端能连接 PostgreSQL。
- 管理员账号可登录。

## 阶段 10：测试、文档与最终验证

目标：用最小但有效的测试覆盖核心风险。

后端测试：

- 登录成功和失败。
- 未登录访问受保护接口。
- 获取和更新备考档案。
- 创建和查询任务。
- 同时只能有一个运行中计时。
- 结束计时生成学习记录。
- 统计接口空数据不报错。

前端验证：

- 登录流程。
- 创建任务。
- 开始并结束计时。
- 查看新生成记录。
- 仪表盘统计刷新。

文档：

- README 项目介绍。
- 本地开发启动命令。
- Docker Compose 启动命令。
- 环境变量说明。
- 默认账号配置说明。

最终验收：

- 本地开发模式能跑。
- Docker Compose 模式能跑。
- 核心流程：登录 -> 创建任务 -> 开始计时 -> 结束计时 -> 查看记录 -> 查看统计。
- 所有新增文件提交到 GitHub。

## 建议开发批次

### 批次 1：可登录的后端和数据库

交付：

- FastAPI 项目骨架
- 数据库连接
- 用户模型
- JWT 登录
- 初始管理员
- 认证测试

### 批次 2：学习业务后端闭环

交付：

- 备考档案
- 每日任务
- 计时
- 学习记录
- 统计
- 周复盘

### 批次 3：前端可用闭环

交付：

- 登录
- 主布局
- 仪表盘
- 计划
- 计时
- 记录
- 复盘
- 设置

### 批次 4：部署和验收

交付：

- Dockerfile
- docker-compose.yml
- README
- 本地验证
- GitHub 推送

## 开发时的风险控制

- 先保证主链路可用，再打磨 UI。
- 统计接口必须能处理空数据。
- 计时状态以服务端为准，避免刷新页面丢失。
- 所有业务接口都要用当前用户过滤数据。
- Docker Compose 先跑通开发可用版本，HTTPS 交给服务器反向代理阶段处理。

