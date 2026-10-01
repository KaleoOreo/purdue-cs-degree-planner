import pytest

from degree_planner.models import Course
from degree_planner.reports import (
    course_codes,
    format_course_choice_group,
    format_required_course_group,
    format_semester_plan,
    total_credits,
)


@pytest.mark.parametrize(
    "remaining_count, options, expected",
    [
        pytest.param(0, {"B"}, ["Choice: satisfied"], id="satisfied"),
        pytest.param(1, {"B", "A"}, ["Choice: 1 additional course required", "Remaining options:", "  A", "  B"], id="one-required"),
        pytest.param(2, {"C", "B"}, ["Choice: 2 additional courses required", "Remaining options:", "  B", "  C"], id="multiple-required"),
    ],
)
def test_format_course_choice_group(remaining_count, options, expected):
    assert format_course_choice_group("Choice", remaining_count, options) == expected


@pytest.mark.parametrize(
    "missing, expected",
    [
        pytest.param(set(), ["Core: no missing required courses"], id="none-missing"),
        pytest.param(
            {"CS 24000", "CS 18200"},
            ["Core: missing required courses", "  CS 18200", "  CS 24000"],
            id="missing-courses-sorted",
        ),
    ],
)
def test_format_required_course_group(missing, expected):
    assert format_required_course_group("Core", missing) == expected


def test_course_codes_returns_codes_in_order():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core"),
    ]

    assert course_codes(courses) == ["CS 18000", "CS 18200"]


def test_total_credits_adds_course_credits():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core"),
    ]

    assert total_credits(courses) == 7


def test_format_semester_plan_shows_courses_and_credit_totals():
    course_b = Course("B", "Course B", 3, "core")
    course_c = Course("C", "Course C", 4, "core")
    course_a = Course("A", "Course A", 3, "core", ["B", "C"])
    lines = format_semester_plan([[course_b, course_c], [course_a]])
    assert lines == [
        "Semester 1 (7 credits)",
        "  B: Course B (3 credits)",
        "  C: Course C (4 credits)",
        "Semester 2 (3 credits)",
        "  A: Course A (3 credits)",
    ]
