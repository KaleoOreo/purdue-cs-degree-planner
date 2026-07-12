from degree_planner.models import Course
from degree_planner.reports import course_codes


def test_course_codes_returns_codes_in_order():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core"),
    ]

    assert course_codes(courses) == ["CS 18000", "CS 18200"]
