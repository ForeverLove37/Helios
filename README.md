# Helios - 一键式远程计算平台

Helios是一个分布式的远程计算平台，允许用户通过简单的命令行界面在远程服务器上执行Python脚本，并提供实时日志流功能。

## 系统架构

Helios由三个核心组件构成：

- **Helios-CLI**: 客户端命令行工具，用于提交任务和接收日志
- **Helios-Manager**: 基于FastAPI的服务端，负责任务管理和WebSocket日志转发
- **Helios-Worker**: 基于RQ和Docker的执行端，在隔离容器中运行任务

## 功能特性

- 🚀 一键式任务提交和执行
- 📦 自动依赖分析和项目打包
- 🔀 优先级队列支持
- 📊 实时日志流
- 🐳 Docker容器隔离
- ⚡ 资源限制控制（CPU、内存）
- 🔄 多Worker并行处理

## 快速开始

### 1. 环境要求

- Python 3.8+
- Docker Engine
- Redis Server

### 2. 使用Docker Compose（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd helios

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 3. 手动安装

#### 安装Redis

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS (使用Homebrew)
brew install redis

# 启动Redis
redis-server
```

#### 安装服务器端

```bash
cd helios_server

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp ../.env.example .env
# 编辑.env文件修改配置

# 启动Manager
./run_server.sh
```

#### 安装Worker

```bash
# 在新的终端窗口中
cd helios_server

# 激活虚拟环境
source venv/bin/activate

# 启动Worker
./run_worker.sh
```

#### 安装CLI客户端

```bash
cd helios_cli

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装CLI工具
pip install -e .
```

## 使用方法

### 基本用法

```bash
# 在你的项目目录下执行
remote-run main.py

# 指定任务名称和优先级
remote-run main.py --name "我的数据处理任务" --priority high

# 设置资源限制
remote-run main.py --cpu-limit 2 --mem-limit 4g

# 指定Manager URL
remote-run main.py --manager-url http://your-server:8000
```

### 项目要求

你的项目应包含：
- Python入口脚本（如`main.py`）
- `requirements.txt`文件（如果没有，CLI会自动生成）

### 示例项目

```python
# main.py
import time
import random

print("开始执行任务...")
for i in range(5):
    print(f"处理步骤 {i+1}/5")
    time.sleep(random.randint(1, 3))

print("任务执行完成！")
```

```bash
# 执行任务
remote-run main.py --name "示例任务"
```

## API文档

启动Helios-Manager后，可以通过以下地址访问API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要端点

- `POST /api/v1/tasks/submit` - 提交新任务
- `GET /api/v1/tasks/{task_id}/status` - 查询任务状态
- `WebSocket /ws/logs/{task_id}` - 实时日志流

## 配置说明

主要配置项（通过环境变量设置）：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `REDIS_HOST` | localhost | Redis服务器地址 |
| `REDIS_PORT` | 6379 | Redis服务器端口 |
| `TASK_STORAGE_PATH` | /var/helios/tasks | 任务文件存储路径 |
| `API_HOST` | 0.0.0.0 | API服务器地址 |
| `API_PORT` | 8000 | API服务器端口 |
| `DOCKER_TIMEOUT` | 3600 | Docker容器超时时间（秒） |

## 开发指南

### 项目结构

```
helios/
├── helios_cli/           # CLI客户端
│   ├── main.py          # 主程序
│   └── requirements.txt # 依赖
├── helios_server/        # 服务器端
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── websocket/   # WebSocket管理
│   │   ├── worker/      # Worker任务
│   │   └── core/        # 核心配置
│   ├── worker.py        # Worker入口
│   ├── run_server.sh    # 服务器启动脚本
│   ├── run_worker.sh    # Worker启动脚本
│   └── Dockerfile       # Docker镜像定义
├── docker-compose.yml    # Docker Compose配置
├── .env.example         # 环境变量模板
└── README.md           # 项目文档
```

### 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 故障排除

### 常见问题

1. **Redis连接失败**
   - 确保Redis服务正在运行
   - 检查防火墙设置
   - 验证连接配置

2. **Docker权限错误**
   - 确保用户在docker组中
   - 检查Docker服务状态

3. **任务执行失败**
   - 查看Worker日志
   - 验证requirements.txt文件
   - 检查入口脚本语法

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f helios-server
docker-compose logs -f helios-worker
```

## 支持

如果你遇到问题或有功能建议，请：

1. 查看[FAQ](docs/FAQ.md)
2. 搜索[Issues](../../issues)
3. 创建新的Issue

---

**Helios** - 让远程计算变得简单高效！