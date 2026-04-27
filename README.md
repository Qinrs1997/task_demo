# Task Management API / 任务管理 API

## 中文说明

这是一个精简的 Python FastAPI 后端示例项目，实现了一个任务管理系统 API。项目结构采用常见的分层习惯，方便对照学习：`api/v1/endpoints` 写接口，`crud` 写数据库操作，`models` 写 SQLAlchemy 模型，`schemas` 写 Pydantic 入参出参，`core/database.py` 负责数据库连接。

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

### 快速开始

从 GitHub 获取代码：

```bash
git clone https://github.com/Qinrs1997/task_demo.git
cd task_demo
scripts\start.bat
```

`scripts\start.bat` 会自动下载并配置运行环境：

- 检查 `conda`
- 创建 `task_demo` 虚拟环境
- 安装 `requirements.txt`
- 从 `config/startup.env` 读取启动配置
- 如果端口被占用，按配置自动结束占用进程
- 从 `.env` 读取应用配置和 API Key
- 启动 FastAPI 服务

### Conda 环境快速配置

如果电脑还没有安装 Conda，先安装 Miniconda：

- Windows 安装说明：https://docs.conda.io/projects/conda/en/stable/user-guide/install/windows.html
- Miniconda 下载说明：https://www.anaconda.com/docs/getting-started/miniconda/install

推荐直接运行快速配置脚本：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\quick_setup.ps1
```

它会引导你配置：

- Conda 环境名
- Python 版本
- 服务端口
- API Key
- 日志文件位置
- 是否自动结束占用端口的进程

一键使用默认值检测，不启动服务：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\quick_setup.ps1 -AcceptDefaults -NoStart
```

启动配置文件：

```text
config/startup.env
```

应用配置文件：

```text
.env
```

日志配置也在 `.env`：

```text
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
ERROR_LOG_FILE=logs/error.log
LOG_TO_CONSOLE=false
```

查看日志：

```powershell
Get-Content .\logs\app.log -Tail 50
Get-Content .\logs\app.log -Wait
```

如果本机 Conda 镜像不可用，可以临时指定 channel：

```bash
set CONDA_CHANNEL_ARGS=--override-channels -c https://repo.anaconda.com/pkgs/main
scripts\start.bat
```

也可以手动执行：

```bash
conda create -n task_demo python=3.10 -y
conda activate task_demo
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

启动后访问：

```text
HTML 测试页面: http://127.0.0.1:8000/ui/
Swagger 文档:   http://127.0.0.1:8000/docs
健康检查:       http://127.0.0.1:8000/health
```

常用启动配置写在 `config/startup.env`：

```text
APP_PORT=8001
APP_RELOAD=false
CONDA_ENV_NAME=task_demo
KILL_PORT_ON_START=true
UVICORN_ACCESS_LOG=false
```

### API Key

接口默认需要请求头：

```text
X-API-Key: dev-secret
```

API Key 可以理解为一个简单的接口访问密码。真实生产项目通常会使用登录、JWT、OAuth2 或权限系统。

### 日志

业务日志默认写入：

```text
logs/app.log
```

错误日志默认写入：

```text
logs/error.log
```

任务完成后的模拟邮件日志会写入 `logs/app.log`，例如：

```text
Email sent for task 1 | title=Prepare FastAPI demo | description=Build a compact task management API | due_date=2026-04-28T08:00:00+00:00 | completed_at=2026-04-27T08:00:00+00:00
```

如果你想在启动窗口显示每个 HTTP 请求，把 `config/startup.env` 改成：

```text
UVICORN_ACCESS_LOG=true
```

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

This is a compact Python FastAPI backend demo. It implements a task management REST API and follows a common layered structure: `api/v1/endpoints` for routes, `crud` for database operations, `models` for SQLAlchemy models, `schemas` for Pydantic request/response schemas, and `core/database.py` for database setup.

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

### Quick Start

Clone the project:

```bash
git clone https://github.com/Qinrs1997/task_demo.git
cd task_demo
scripts\start.bat
```

`scripts\start.bat` will download and configure the runtime environment:

- check `conda`
- create the `task_demo` virtual environment
- install `requirements.txt`
- read startup options from `config/startup.env`
- kill the process occupying the configured port when enabled
- read app settings and API Key from `.env`
- start the FastAPI server

### Conda Environment Quick Setup

If Conda is not installed yet, install Miniconda first:

- Windows install guide: https://docs.conda.io/projects/conda/en/stable/user-guide/install/windows.html
- Miniconda download guide: https://www.anaconda.com/docs/getting-started/miniconda/install

Recommended setup command:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\quick_setup.ps1
```

It guides you through:

- Conda environment name
- Python version
- service port
- API Key
- log file paths
- whether to kill the process occupying the configured port

Run with defaults without starting the server:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\quick_setup.ps1 -AcceptDefaults -NoStart
```

Startup config:

```text
config/startup.env
```

Application config:

```text
.env
```

Logging config also lives in `.env`:

```text
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
ERROR_LOG_FILE=logs/error.log
LOG_TO_CONSOLE=false
```

View logs:

```powershell
Get-Content .\logs\app.log -Tail 50
Get-Content .\logs\app.log -Wait
```

If your local Conda mirror is unavailable, specify a channel:

```bash
set CONDA_CHANNEL_ARGS=--override-channels -c https://repo.anaconda.com/pkgs/main
scripts\start.bat
```

Manual setup:

```bash
conda create -n task_demo python=3.10 -y
conda activate task_demo
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open these URLs after startup:

```text
HTML test UI: http://127.0.0.1:8000/ui/
Swagger docs: http://127.0.0.1:8000/docs
Health check: http://127.0.0.1:8000/health
```

Common startup options live in `config/startup.env`:

```text
APP_PORT=8001
APP_RELOAD=false
CONDA_ENV_NAME=task_demo
KILL_PORT_ON_START=true
UVICORN_ACCESS_LOG=false
```

### API Key

Protected endpoints require this request header by default:

```text
X-API-Key: dev-secret
```

The API Key is a simple access password for this demo. In production systems, authentication is usually handled with login sessions, JWT, OAuth2, or a full permission system.

### Logging

Application logs are written to:

```text
logs/app.log
```

Error logs are written to:

```text
logs/error.log
```

The mock email notification log is written to `logs/app.log`, for example:

```text
Email sent for task 1 | title=Prepare FastAPI demo | description=Build a compact task management API | due_date=2026-04-28T08:00:00+00:00 | completed_at=2026-04-27T08:00:00+00:00
```

To show every HTTP request in the startup console, set this in `config/startup.env`:

```text
UVICORN_ACCESS_LOG=true
```

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
