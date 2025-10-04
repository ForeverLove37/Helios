# Helios CLI

Helios CLI是Helios一键式远程计算平台的客户端工具，用于提交任务到远程服务器并实时查看日志输出。

## 功能特性

- 🚀 一键式任务提交和执行
- 📦 自动依赖分析和项目打包  
- 🔀 优先级队列支持
- 📊 实时日志流
- ⚡ 资源限制控制（CPU、内存）

## 安装

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/ForeverLove37/Helios.git
cd Helios
git checkout helios-cli

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r helios_cli/requirements.txt

# 安装CLI工具
pip install -e .
```

### 使用pip安装

```bash
pip install helios-cli
```

## 使用方法

### 基本用法

```bash
# 在你的项目目录下执行
helios-cli main.py

# 指定任务名称和优先级
helios-cli main.py --name "我的数据处理任务" --priority high

# 设置资源限制
helios-cli main.py --cpu-limit 2 --mem-limit 4g

# 指定Manager URL
helios-cli main.py --manager-url http://your-server:8000
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
helios-cli main.py --name "示例任务"
```

## 配置

CLI工具可以通过以下方式配置：

### 环境变量

```bash
export HELIOS_MANAGER_URL=http://localhost:8000
export HELIOS_DEFAULT_PRIORITY=default
```

### 配置文件

创建 `~/.helios/config.yaml`:

```yaml
manager_url: http://localhost:8000
default_priority: default
default_cpu_limit: 1
default_mem_limit: 2g
```

## 开发

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/ForeverLove37/Helios.git
cd Helios
git checkout helios-cli

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black helios_cli/
isort helios_cli/
```

### 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

如果你遇到问题或有功能建议，请：

1. 查看[FAQ](../../docs/FAQ.md)
2. 搜索[Issues](../../issues)
3. 创建新的Issue

---

**Helios CLI** - 让远程计算变得简单高效！