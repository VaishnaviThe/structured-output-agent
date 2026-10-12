from pydantic import BaseModel, ConfigDict, Field


class Job(BaseModel):
    """Schema representing a job listing."""

    model_config = ConfigDict(extra="forbid", strict=True)

    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: str = Field(min_length=1)
    experience_years: int = Field(ge=0, le=50)


class JobSearchResult(BaseModel):
    """Structured result returned by the agent."""

    model_config = ConfigDict(extra="forbid", strict=True)

    jobs: list[Job] = Field(min_length=1, max_length=10)

class ToolResponse(BaseModel):
    """Standard structure for validated tool responses."""

    model_config = ConfigDict(extra="forbid", strict=True)

    tool_name: str = Field(min_length=1)
    success: bool
    data: dict