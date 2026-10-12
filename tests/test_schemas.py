import pytest

from pydantic import ValidationError

from app.schemas import Job, JobSearchResult


def test_valid_job():
    job = Job(
        title="Python Developer",
        company="Example Corp",
        location="Remote",
        experience_years=2,
    )

    assert job.title == "Python Developer"
    assert job.experience_years == 2


def test_rejects_string_for_integer():
    with pytest.raises(ValidationError):
        Job(
            title="Python Developer",
            company="Example Corp",
            location="Remote",
            experience_years="two",
        )


def test_rejects_negative_experience():
    with pytest.raises(ValidationError):
        Job(
            title="Python Developer",
            company="Example Corp",
            location="Remote",
            experience_years=-1,
        )


def test_rejects_extra_fields():
    with pytest.raises(ValidationError):
        Job(
            title="Python Developer",
            company="Example Corp",
            location="Remote",
            experience_years=2,
            salary="10 LPA",
        )


def test_valid_job_search_result():
    result = JobSearchResult(
        jobs=[
            {
                "title": "Python Developer",
                "company": "Example Corp",
                "location": "Remote",
                "experience_years": 2,
            }
        ]
    )

    assert len(result.jobs) == 1
    assert result.jobs[0].company == "Example Corp"


def test_rejects_empty_job_list():
    with pytest.raises(ValidationError):
        JobSearchResult(jobs=[])