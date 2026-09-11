from degree_planner.models import Course
from degree_planner.validation import find_missing_prerequisites


def test_find_missing_prerequisites_returns_unknown_prerequisite_codes():
    courses = [
        Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]),
    ]

    assert find_missing_prerequisites(courses) == ["CS 18000"]
