from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Job(BaseModel):
    """Schema representing a job listing."""

    model_config = ConfigDict(extra="forbid", strict=True)

    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: str = Field(min_length=1)
    experience_years: int = Field(ge=0, le=50)


class JobSearchResult(BaseModel):
    """Structured result returned by the job-search agent."""

    model_config = ConfigDict(extra="forbid", strict=True)

    jobs: list[Job] = Field(min_length=1, max_length=10)


class TaskPriority(str, Enum):
    """Allowed task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    """Allowed task statuses."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskSummary(BaseModel):
    """Structured summary of a task."""

    model_config = ConfigDict(extra="forbid", strict=True)

    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    priority: TaskPriority
    status: TaskStatus


class ToolResponse(BaseModel):
    """Standard structure for validated tool responses."""

    model_config = ConfigDict(extra="forbid", strict=True)

    tool_name: str = Field(min_length=1)
    success: bool
    data: dict