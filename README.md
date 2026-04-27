# Task Management API / 任务管理 API

## 中文说明

这是一个用于 Python 后端面试题的精简 FastAPI 项目，实现了一个任务管理系统 API。项目结构刻意贴近 `base-apivue/backend` 的分层习惯，方便对照学习：`api/v1/endpoints` 写接口，`crud` 写数据库操作，`models` 写 SQLAlchemy 模型，`schemas` 写 Pydantic 入参出参，`core/database.py` 负责数据库连接。

### 功能特性

- FastAPI RESTful API
- SQLite + SQLAlchemy Async ORM
- 任务增删改查
- 按任务状态筛选
- `limit / offset` 分页
- API Key 简单认证
- `due_date` 必须是未来时间
- 任务完成时触发异步模拟邮件通知
- 统一响应格式 `Response`
- 简单 HTML 测试页面
- pytest 自动化测试

### 项目结构

```text
app/
  api/
    deps.py
    v1/
      router.py
      endpoints/
        tasks.py
  core/
    config.py
    database.py
    exceptions.py
    logging.py
  crud/
    base.py
    task.py
  models/
    base.py
    task.py
  schemas/
    response.py
    task.py
  services/
    notification_service.py
  static/
    index.html
  main.py
tests/
  conftest.py
  test_tasks_api.py
```

### 本地启动

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload
```

Windows 可以直接运行：

```bash
scripts\start.bat
```

启动后访问：

```text
HTML 测试页面: http://127.0.0.1:8000/ui/
Swagger 文档:   http://127.0.0.1:8000/docs
健康检查:       http://127.0.0.1:8000/health
```

### API Key

接口默认需要请求头：

```text
X-API-Key: dev-secret
```

API Key 可以理解为一个简单的接口访问密码。真实生产项目通常会使用登录、JWT、OAuth2 或权限系统。

### 接口列表

```text
POST   /api/v1/tasks              创建任务
GET    /api/v1/tasks              任务列表，支持 status、limit、offset
GET    /api/v1/tasks/{task_id}    任务详情
PUT    /api/v1/tasks/{task_id}    更新任务，完成任务时触发异步通知
DELETE /api/v1/tasks/{task_id}    删除任务
```

### 运行测试

```bash
pytest
pytest --cov=app --cov-report=term-missing
```

---

## English Version

This is a compact FastAPI project for a Python backend interview task. It implements a task management REST API and follows a layered structure similar to `base-apivue/backend`: `api/v1/endpoints` for routes, `crud` for database operations, `models` for SQLAlchemy models, `schemas` for Pydantic request/response schemas, and `core/database.py` for database setup.

### Features

- FastAPI RESTful API
- SQLite + SQLAlchemy Async ORM
- Task CRUD
- Status filtering
- `limit / offset` pagination
- Simple API Key authentication
- Future-only `due_date` validation
- Async mock email notification when a task is completed
- Unified `Response` schema
- Simple HTML test UI
- pytest test suite

### Project Structure

```text
app/
  api/
    deps.py
    v1/
      router.py
      endpoints/
        tasks.py
  core/
    config.py
    database.py
    exceptions.py
    logging.py
  crud/
    base.py
    task.py
  models/
    base.py
    task.py
  schemas/
    response.py
    task.py
  services/
    notification_service.py
  static/
    index.html
  main.py
tests/
  conftest.py
  test_tasks_api.py
```

### Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload
```

On Windows, you can also run:

```bash
scripts\start.bat
```

Open these URLs after startup:

```text
HTML test UI: http://127.0.0.1:8000/ui/
Swagger docs: http://127.0.0.1:8000/docs
Health check: http://127.0.0.1:8000/health
```

### API Key

Protected endpoints require this request header by default:

```text
X-API-Key: dev-secret
```

The API Key is a simple access password for this demo. In production systems, authentication is usually handled with login sessions, JWT, OAuth2, or a full permission system.

### API Endpoints

```text
POST   /api/v1/tasks              Create a task
GET    /api/v1/tasks              List tasks with status, limit, and offset
GET    /api/v1/tasks/{task_id}    Get task detail
PUT    /api/v1/tasks/{task_id}    Update a task and trigger async notification on completion
DELETE /api/v1/tasks/{task_id}    Delete a task
```

### Run Tests

```bash
pytest
pytest --cov=app --cov-report=term-missing
```
