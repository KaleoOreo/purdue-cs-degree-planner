import pytest
from pydantic import ValidationError

from degree_planner.schemas import (
    CourseCompletionRequest,
    CourseResponse,
    CurriculumProgressResponse,
)


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


def test_curriculum_progress_response_preserves_required_group_definition():
    response = CurriculumProgressResponse(
        name="Software Engineering",
        is_complete=False,
        completed_course_codes=["CS 18000"],
        required_groups=[{
            "name": "Computer Science Core",
            "course_codes": ["CS 18000", "CS 18200"],
            "missing_course_codes": ["CS 18200"],
        }],
        choice_groups=[],
        option_groups=[],
        allocations=None,
    )

    assert response.required_groups[0].course_codes == ["CS 18000", "CS 18200"]
    assert response.required_groups[0].missing_course_codes == ["CS 18200"]
