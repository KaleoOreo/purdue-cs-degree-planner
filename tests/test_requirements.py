import pytest

from degree_planner.requirements import (
    CourseChoiceGroup,
    RequiredCourseGroup,
    find_missing_required_courses,
)


def test_find_missing_required_courses_ignores_unrelated_completions():
    required = {"CS 18000", "CS 18200", "CS 24000"}
    completed = {"CS 18000", "CS 18200", "OTHER 10000"}
    missing = find_missing_required_courses(required, completed)
    assert missing == {"CS 24000"}


def test_find_missing_required_courses_returns_empty_when_all_completed():
    required = {"CS 18000", "CS 18200"}
    completed = {"CS 18000", "CS 18200", "OTHER 10000"}
    missing = find_missing_required_courses(required, completed)
    assert missing == set()


def test_required_course_groups_check_their_own_course_codes():
    first = RequiredCourseGroup("First group", {"A", "B"})
    second = RequiredCourseGroup("Second group", {"B", "C"})
    completed = {"B"}
    assert first.missing_courses(completed) == {"A"}
    assert second.missing_courses(completed) == {"C"}
    assert first.course_codes == {"A", "B"}
    assert second.course_codes == {"B", "C"}


def test_required_course_group_is_satisfied_only_after_all_courses_completed():
    group = RequiredCourseGroup("Example group", {"A", "B"})
    completed = {"A"}
    assert group.is_satisfied(completed) is False
    completed.add("B")
    assert group.is_satisfied(completed) is True


@pytest.mark.parametrize(
    "completed, expected",
    [
        pytest.param({"A", "X"}, 1, id="partial-completion"),
        pytest.param({"A", "C", "X"}, 0, id="exactly-enough"),
        pytest.param({"A", "B", "C"}, 0, id="extra-completions"),
    ],
)
def test_course_choice_group_counts_remaining_choices(completed, expected):
    group = CourseChoiceGroup("Example elective", {"A", "B", "C"}, 2)
    assert group.remaining_count(completed) == expected
