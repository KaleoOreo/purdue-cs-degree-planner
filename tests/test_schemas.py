import pytest
from pydantic import ValidationError

from degree_planner.schemas import CourseCompletionRequest, CourseResponse


def test_course_completion_request_requires_course_code():
    with pytest.raises(ValidationError):
        CourseCompletionRequest.model_validate({})


def test_course_response_rejects_invalid_credits():
    with pytest.raises(ValidationError):
        CourseResponse(
            code="CS 18000",
            title="Problem Solving and Object-Oriented Programming",
            credits="four",  # type: ignore[arg-type]
            category="core",
            prerequisites=[],
        )
