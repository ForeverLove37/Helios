"""Helios CLI - Remote command execution client."""

import json
import os
import sys
import zipfile
from pathlib import Path
from typing import Optional

import requests
import typer
import websockets
from pipreqs import pipreqs

# Import configuration from server module
server_path = os.path.join(os.path.dirname(__file__), "..", "helios_server")
if server_path not in sys.path:
    sys.path.append(server_path)

try:
    from app.core.constants import TaskPriority, TaskSignals
except ImportError:
    # Fallback definitions if server module is not available
    class TaskPriority(str):
        HIGH = "high"
        DEFAULT = "default"
    
    class TaskSignals:
        COMPLETE = "[HELIOS_TASK_COMPLETE]"
        FAILED_PREFIX = "[HELIOS_TASK_FAILED"


class HeliosClient:
    """Helios client for remote task execution."""
    
    def __init__(self, manager_url: str):
        """Initialize client with manager URL."""
        self.manager_url = manager_url.rstrip("/")
        self.session = requests.Session()
    
    def discover_dependencies(self, project_path: str) -> None:
        """Automatically discover project dependencies and generate requirements.txt."""
        try:
            typer.echo("🔍 正在分析项目依赖...")
            pipreqs.init(
                project_path,
                encoding="utf-8",
                save_path="requirements.txt",
                print_only=False,
                force=False,
                ignore=False,
                exclude=None,
                include_only=None,
                proxy=None,
                pypi_server=None,
                dry_run=False,
                interactive=False,
                extra_ignore_dirs=None,
                use_local_version=None,
                extra_index_urls=None,
                ignore_local_version=None,
                no_fail=False,
                no_include_pin=False,
                save_py=None,
                use_pep621=None,
                pep621_dependencies_path=None,
                format_plain=None,
                debug=False
            )
            typer.echo("✅ 依赖分析完成")
        except Exception as e:
            typer.echo(f"⚠️ 依赖分析警告: {e}", err=True)
    
    def create_project_zip(self, project_path: str) -> str:
        """Create a zip file of the project directory."""
        typer.echo("📦 项目打包中...")
        
        zip_path = os.path.join(project_path, "helios_project.zip")
        
        # Check for .gitignore to exclude files
        gitignore_path = os.path.join(project_path, ".gitignore")
        exclude_patterns = {".git", "__pycache__", "*.pyc", ".DS_Store"}
        
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                exclude_patterns.update(line.strip() for line in f if line.strip() and not line.startswith("#"))
        
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_patterns]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    # Skip excluded files
                    if any(file.endswith(pattern.replace("*", "")) for pattern in exclude_patterns):
                        continue
                    
                    # Calculate relative path from project_path
                    arcname = os.path.relpath(file_path, project_path)
                    zipf.write(file_path, arcname)
        
        typer.echo("✅ 项目打包完成")
        return zip_path
    
    def submit_task(
        self,
        zip_path: str,
        entrypoint: str,
        priority: TaskPriority = TaskPriority.DEFAULT,
        name: Optional[str] = None,
        cpu_limit: Optional[int] = None,
        mem_limit: Optional[str] = None
    ) -> str:
        """Submit task to Helios manager."""
        typer.echo("📤 正在上传任务...")
        
        # Prepare metadata
        metadata = {
            "entrypoint": entrypoint,
            "priority": priority,
            "name": name or f"helios-task-{os.path.basename(os.getcwd())}",
            "resources": {}
        }
        
        if cpu_limit is not None:
            metadata["resources"]["cpu"] = cpu_limit
        if mem_limit is not None:
            metadata["resources"]["mem"] = mem_limit
        
        # Prepare files for upload
        files = {
            "file": (os.path.basename(zip_path), open(zip_path, "rb"), "application/zip"),
            "metadata": (None, json.dumps(metadata), "application/json")
        }
        
        try:
            response = self.session.post(
                f"{self.manager_url}/api/v1/tasks/submit",
                files=files,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                typer.echo("✅ 任务提交成功")
                return result.get("task_id")
            else:
                typer.echo(f"❌ 任务提交失败: {result.get('message', 'Unknown error')}")
                raise typer.Exit(1)
                
        except requests.exceptions.RequestException as e:
            typer.echo(f"❌ 网络错误: {e}")
            raise typer.Exit(1)
        finally:
            if isinstance(files["file"], tuple):
                files["file"][1].close()
            else:
                files["file"].close()
    
    async def stream_logs(self, task_id: str) -> None:
        """Stream real-time logs from the task."""
        typer.echo(f"🔄 连接到实时日志流 (Task ID: {task_id})...")
        
        try:
            websocket_url = self.manager_url.replace("http://", "ws://").replace("https://", "wss://")
            async with websockets.connect(f"{websocket_url}/ws/logs/{task_id}") as websocket:
                typer.echo("✅ 已连接到日志流")
                typer.echo("=" * 50)
                
                async for message in websocket:
                    if message == TaskSignals.COMPLETE:
                        typer.echo("=" * 50)
                        typer.echo("✅ 任务执行完成")
                        break
                    elif message.startswith(TaskSignals.FAILED_PREFIX):
                        typer.echo("=" * 50)
                        typer.echo(f"❌ 任务执行失败: {message}")
                        break
                    else:
                        print(message)
                        
        except websockets.exceptions.ConnectionClosed:
            typer.echo("🔌 连接已断开")
        except Exception as e:
            typer.echo(f"❌ 日志流错误: {e}")


app = typer.Typer(
    name="remote-run",
    help="Helios - 一键式远程计算平台客户端",
    add_completion=False
)


@app.callback()
def main():
    """Helios CLI - 远程任务执行工具."""
    pass


@app.command()
def remote_run(
    entrypoint: str = typer.Argument(..., help="入口脚本文件名 (例如: main.py)"),
    priority: TaskPriority = typer.Option(
        TaskPriority.DEFAULT,
        "--priority",
        "-p",
        help="任务优先级"
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="任务名称"
    ),
    cpu_limit: Optional[int] = typer.Option(
        None,
        "--cpu-limit",
        "-c",
        help="CPU核心数限制"
    ),
    mem_limit: Optional[str] = typer.Option(
        None,
        "--mem-limit",
        "-m",
        help="内存限制 (例如: 4g, 512m)"
    ),
    manager_url: str = typer.Option(
        "http://localhost:8000",
        "--manager-url",
        "-u",
        help="Helios Manager URL"
    )
):
    """在远程服务器上执行指定的脚本."""
    
    # Initialize client
    client = HeliosClient(manager_url)
    
    # Get current working directory
    project_path = os.getcwd()
    
    try:
        # Step 1: Discover dependencies
        client.discover_dependencies(project_path)
        
        # Step 2: Create project zip
        zip_path = client.create_project_zip(project_path)
        
        # Step 3: Submit task
        task_id = client.submit_task(
            zip_path,
            entrypoint,
            priority,
            name,
            cpu_limit,
            mem_limit
        )
        
        # Step 4: Stream logs
        import asyncio
        asyncio.run(client.stream_logs(task_id))
        
    except KeyboardInterrupt:
        typer.echo("\n👋 用户中断操作")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ 执行错误: {e}")
        raise typer.Exit(1)
    finally:
        # Clean up zip file
        if os.path.exists(zip_path):
            os.remove(zip_path)


if __name__ == "__main__":
    app()