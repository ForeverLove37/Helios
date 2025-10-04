# Helios Server

Helios Server是Helios一键式远程计算平台的服务器端组件，提供任务管理、WebSocket日志转发和Docker容器执行功能。

## 功能特性

- 🚀 FastAPI异步任务管理API
- 📊 WebSocket实时日志转发
- 🐳 Docker容器隔离执行
- 🔀 多优先级任务队列支持
- ⚡ 资源限制控制
- 🔄 分布式Worker支持

## 架构组件

### Helios Manager (FastAPI)
- RESTful API端点
- WebSocket连接管理
- 任务生命周期管理
- 实时日志转发

### Helios Worker (RQ + Docker)
- 任务队列处理
- Docker容器执行
- 日志收集和发布
- 资源清理

## 安装部署

### 使用Docker Compose (推荐)

```bash
# 克隆仓库
git clone https://github.com/ForeverLove37/Helios.git
cd Helios
git checkout helios-server

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 手动安装

#### 环境要求

- Python 3.8+
- Redis Server
- Docker Engine

#### 安装步骤

```bash
# 安装Redis
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis

# 启动Redis
redis-server

# 安装服务器
cd helios_server

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp ../.env.example .env

# 启动Manager
./run_server.sh

# 启动Worker (新终端)
./run_worker.sh
```

## API文档

启动服务后可通过以下地址访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要端点

- `POST /api/v1/tasks/submit` - 提交新任务
- `GET /api/v1/tasks/{task_id}/status` - 查询任务状态
- `WebSocket /ws/logs/{task_id}` - 实时日志流

## 配置说明

主要配置项（通过环境变量或`.env`文件设置）：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `REDIS_HOST` | localhost | Redis服务器地址 |
| `REDIS_PORT` | 6379 | Redis服务器端口 |
| `TASK_STORAGE_PATH` | /var/helios/tasks | 任务文件存储路径 |
| `API_HOST` | 0.0.0.0 | API服务器地址 |
| `API_PORT` | 8000 | API服务器端口 |
| `DOCKER_TIMEOUT` | 3600 | Docker容器超时时间（秒） |

## 项目结构

```
helios_server/
├── app/
│   ├── api/         # API路由和模型
│   ├── websocket/   # WebSocket连接管理
│   ├── worker/      # Worker任务定义
│   ├── core/        # 核心配置和常量
│   └── main.py      # FastAPI应用入口
├── worker.py        # Worker进程入口
├── run_server.sh    # Manager启动脚本
├── run_worker.sh    # Worker启动脚本
├── Dockerfile       # Docker镜像定义
└── requirements.txt # Python依赖
```

## 开发

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/ForeverLove37/Helios.git
cd Helios
git checkout helios-server

# 安装开发依赖
pip install -r requirements.txt
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black app/ worker.py
isort app/ worker.py
```

### 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 监控和日志

### 查看服务日志

```bash
# Docker Compose
docker-compose logs -f helios-server
docker-compose logs -f helios-worker

# 手动部署
# Manager日志在终端直接输出
# Worker日志在终端直接输出
```

### 监控指标

- Redis连接状态
- 任务队列长度
- Worker进程状态
- Docker容器使用情况

## 故障排除

### 常见问题

1. **Redis连接失败**
   - 检查Redis服务状态
   - 验证连接配置

2. **Docker权限错误**
   - 确保用户在docker组中
   - 检查Docker服务状态

3. **任务执行失败**
   - 查看Worker日志
   - 验证Docker镜像可用性

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

如果你遇到问题或有功能建议，请：

1. 查看[FAQ](../../docs/FAQ.md)
2. 搜索[Issues](../../issues)
3. 创建新的Issue

---

**Helios Server** - 强大的远程计算后端服务！