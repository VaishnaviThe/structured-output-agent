import pytest
from pydantic import ValidationError

from app.schemas import TaskPriority, TaskStatus, TaskSummary


def test_valid_task_summary():
    task = TaskSummary(
        title="Fix login bug",
        description="Resolve the issue preventing users from signing in.",
        priority=TaskPriority.HIGH,
        status=TaskStatus.PENDING,
    )

    assert task.title == "Fix login bug"
    assert task.priority == TaskPriority.HIGH
    assert task.status == TaskStatus.PENDING


def test_rejects_invalid_priority():
    with pytest.raises(ValidationError):
        TaskSummary(
            title="Fix login bug",
            description="Resolve the login issue.",
            priority="urgent",
            status=TaskStatus.PENDING,
        )


def test_rejects_invalid_status():
    with pytest.raises(ValidationError):
        TaskSummary(
            title="Fix login bug",
            description="Resolve the login issue.",
            priority=TaskPriority.HIGH,
            status="blocked",
        )


def test_rejects_missing_required_field():
    with pytest.raises(ValidationError):
        TaskSummary(
            title="Fix login bug",
            description="Resolve the login issue.",
            priority=TaskPriority.HIGH,
        )


def test_rejects_extra_fields():
    with pytest.raises(ValidationError):
        TaskSummary(
            title="Fix login bug",
            description="Resolve the login issue.",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            owner="Vaishnavi",
        )


def test_rejects_empty_title():
    with pytest.raises(ValidationError):
        TaskSummary(
            title="",
            description="Resolve the login issue.",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
        )