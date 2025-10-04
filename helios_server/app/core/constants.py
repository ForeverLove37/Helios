"""Constants for Helios project."""

from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    HIGH = "high"
    DEFAULT = "default"


class QueueNames:
    """RQ queue names."""
    HIGH = "high"
    DEFAULT = "default"


class RedisChannels:
    """Redis Pub/Sub channel patterns."""
    LOGS_PREFIX = "logs:"


class TaskSignals:
    """Task completion signals."""
    COMPLETE = "[HELIOS_TASK_COMPLETE]"
    FAILED_PREFIX = "[HELIOS_TASK_FAILED"


class DockerSettings:
    """Docker-related settings."""
    CONTAINER_WORK_DIR = "/app"
    MOUNT_POINT = "/app"
    AUTO_REMOVE = True