"""WebSocket manager for real-time log streaming."""

import asyncio
import json
from typing import Dict, Set

import redis
from fastapi import WebSocket, WebSocketDisconnect

from app.core.config import get_settings
from app.core.constants import RedisChannels


class ConnectionManager:
    """Manages WebSocket connections and log forwarding."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, task_id: str):
        """Connect WebSocket for task log streaming."""
        await websocket.accept()
        
        if task_id not in self.active_connections:
            self.active_connections[task_id] = set()
        
        self.active_connections[task_id].add(websocket)
        
        # Start log forwarding task
        asyncio.create_task(self.forward_logs(task_id))
    
    def disconnect(self, websocket: WebSocket, task_id: str):
        """Disconnect WebSocket connection."""
        if task_id in self.active_connections:
            self.active_connections[task_id].discard(websocket)
            
            # Clean up empty task connection sets
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket."""
        try:
            await websocket.send_text(message)
        except Exception:
            # Connection might be closed, remove it
            pass
    
    async def forward_logs(self, task_id: str):
        """Forward logs from Redis to connected WebSockets."""
        if task_id not in self.active_connections:
            return
        
        channel_name = f"{RedisChannels.LOGS_PREFIX}{task_id}"
        
        try:
            settings = get_settings()
            redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True
            )
            pubsub = redis_client.pubsub()
            pubsub.subscribe(channel_name)
            
            for message in pubsub.listen():
                if message['type'] == 'message':
                    log_line = message['data']
                    
                    # Send to all connected WebSockets for this task
                    disconnected = set()
                    for websocket in self.active_connections[task_id].copy():
                        try:
                            await websocket.send_text(log_line)
                        except Exception:
                            disconnected.add(websocket)
                    
                    # Remove disconnected WebSockets
                    for websocket in disconnected:
                        self.disconnect(websocket, task_id)
                
                # Stop if no more connections for this task
                if task_id not in self.active_connections:
                    break
                    
        except Exception as e:
            print(f"Error forwarding logs for task {task_id}: {e}")
        finally:
            try:
                pubsub.close()
            except:
                pass


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for log streaming."""
    await manager.connect(websocket, task_id)
    try:
        while True:
            # Keep connection alive and handle ping/pong
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)
    except Exception as e:
        print(f"WebSocket error for task {task_id}: {e}")
        manager.disconnect(websocket, task_id)