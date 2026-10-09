import pytest

from degree_planner.models import Course
from degree_planner.planning import (
    build_dependents,
    build_semester_plan,
    calculate_dependency_depths,
    choose_best_semester_combination,
    count_unfinished_prerequisites,
    find_available_courses,
    find_valid_semester_combinations,
    plan_multiple_semesters,
    plan_next_semester,
    prioritize_courses_by_depth,
    topological_sort,
)


def test_calculate_dependency_depths_uses_longest_branch():
    courses = [
        Course("A", "Course A", 3, "core"),
        Course("B", "Course B", 3, "core", ["A"]),
        Course("C", "Course C", 3, "core", ["A"]),
        Course("D", "Course D", 3, "core", ["B"]),
        Course("E", "Course E", 3, "core", ["C"]),
        Course("F", "Course F", 3, "core", ["E"]),
    ]

    assert calculate_dependency_depths(courses) == {
        "A": 3, "B": 1, "C": 2, "D": 0, "E": 1, "F": 0,
    }


def test_prioritize_courses_by_depth_places_deeper_courses_first():
    courses = [
        Course("B", "Course B", 3, "core"),
        Course("A", "Course A", 3, "core"),
        Course("C", "Course C", 3, "core"),
    ]
    depths = {"A": 2, "B": 0, "C": 1}

    prioritized = prioritize_courses_by_depth(courses, depths)

    assert [course.code for course in prioritized] == ["A", "C", "B"]


def test_find_valid_semester_combinations_respects_credit_limit():
    courses = [
        Course("A", "Course A", 4, "core"),
        Course("B", "Course B", 1, "core"),
        Course("C", "Course C", 2, "core"),
        Course("E", "Course E", 5, "core"),
    ]

    combinations = find_valid_semester_combinations(courses, max_credits=6)
    codes = {
        frozenset(course.code for course in combination)
        for combination in combinations
    }

    assert codes == {
        frozenset({"A"}), frozenset({"B"}), frozenset({"C"}), frozenset({"E"}),
        frozenset({"A", "B"}), frozenset({"A", "C"}),
        frozenset({"B", "C"}), frozenset({"B", "E"}),
    }


def test_choose_best_combination_balances_depth_and_credits():
    courses = [
        Course("A", "Course A", 4, "core"),
        Course("B", "Course B", 1, "core"),
        Course("C", "Course C", 2, "core"),
        Course("E", "Course E", 5, "core"),
    ]
    combinations = find_valid_semester_combinations(courses, max_credits=6)
    depths = {"A": 3, "B": 2, "C": 1, "E": 0}

    best = choose_best_semester_combination(combinations, depths)

    assert [course.code for course in best] == ["A", "C"]


def test_plan_multiple_semesters_prioritizes_long_dependency_chain():
    courses = [
        Course("A", "Course A", 3, "core"),
        Course("B", "Course B", 3, "core"),
        Course("C", "Course C", 3, "core", ["A"]),
        Course("D", "Course D", 3, "core", ["C"]),
        Course("E", "Course E", 3, "core"),
    ]

    plan = plan_multiple_semesters(courses, completed=set(), max_credits=6)

    semester_by_course = {
        course.code: index
        for index, semester in enumerate(plan)
        for course in semester
    }
    assert len(plan) == 3
    assert semester_by_course["A"] == 0
    assert semester_by_course["C"] == 1
    assert semester_by_course["D"] == 2


def test_plan_multiple_semesters_selects_best_credit_combination():
    courses = [
        Course("E", "Course E", 5, "core"),
        Course("C", "Course C", 2, "core"),
        Course("B", "Course B", 1, "core"),
        Course("A", "Course A", 4, "core"),
        Course("A1", "Course A1", 3, "core", ["A"]),
        Course("A2", "Course A2", 3, "core", ["A1"]),
        Course("A3", "Course A3", 3, "core", ["A2"]),
        Course("B1", "Course B1", 3, "core", ["B"]),
        Course("B2", "Course B2", 3, "core", ["B1"]),
        Course("C1", "Course C1", 3, "core", ["C"]),
    ]

    plan = plan_multiple_semesters(courses, completed=set(), max_credits=6)

    assert [course.code for course in plan[0]] == ["A", "C"]


def test_depth_priority_respects_already_completed_courses():
    courses = [
        Course("A", "Course A", 3, "core"),
        Course("B", "Course B", 3, "core"),
        Course("C", "Course C", 3, "core", ["A"]),
        Course("D", "Course D", 3, "core", ["C"]),
        Course("E", "Course E", 3, "core"),
    ]
    completed = {"A"}

    plan = plan_multiple_semesters(courses, completed, max_credits=6)

    semester_by_course = {
        course.code: index
        for index, semester in enumerate(plan)
        for course in semester
    }
    assert len(plan) == 2
    assert set(semester_by_course) == {"B", "C", "D", "E"}
    assert semester_by_course["C"] < semester_by_course["D"]
    assert completed == {"A"}


def test_find_available_courses_excludes_locked_courses():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]),
    ]

    available = find_available_courses(courses, set())

    assert [course.code for course in available] == ["CS 18000"]


def test_find_available_courses_excludes_completed_courses():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]),
    ]

    available = find_available_courses(courses, {"CS 18000"})

    assert [course.code for course in available] == ["CS 18200"]


def test_find_available_courses_requires_all_prerequisites():
    courses = [
        Course("CS 24000", "Programming in C", 3, "core", ["CS 18000", "CS 18200"]),
    ]

    available = find_available_courses(courses, {"CS 18000"})

    assert available == []


def test_build_semester_plan_respects_max_credits():
    available = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core"),
    ]

    plan = build_semester_plan(available, max_credits=6)

    assert [course.code for course in plan] == ["CS 18000"]


def test_build_semester_plan_allows_exact_credit_limit():
    available = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core"),
    ]

    plan = build_semester_plan(available, max_credits=7)

    assert [course.code for course in plan] == ["CS 18000", "CS 18200"]


def test_build_semester_plan_rejects_zero_max_credits():
    with pytest.raises(ValueError):
        build_semester_plan([], max_credits=0)


def test_plan_next_semester_filters_then_applies_credit_limit():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]),
        Course("CS 24000", "Programming in C", 3, "core", ["CS 18000", "CS 18200"]),
    ]

    plan = plan_next_semester(courses, {"CS 18000"}, max_credits=3)

    assert [course.code for course in plan] == ["CS 18200"]


def test_build_dependents_groups_courses_by_prerequisite():
    courses = [
        Course("A", "Course A", 3, "core", ["C"]),
        Course("E", "Course E", 3, "core", ["C"]),
        Course("C", "Course C", 3, "core"),
    ]
    dependents = build_dependents(courses)
    assert dependents == {
        "A": [],
        "E": [],
        "C": ["A", "E"],
    }


def test_count_unfinished_prerequisites_excludes_completed():
    courses = [
        Course("A", "Course A", 3, "core", ["B", "C"]),
        Course("B", "Course B", 3, "core"),
        Course("C", "Course C", 3, "core"),
    ]
    counts = count_unfinished_prerequisites(courses, {"B"})
    assert counts == {"A": 1, "B": 0, "C": 0}


def test_topological_sort_places_prerequisite_first():
    courses = [
        Course("A", "Course A", 3, "core", ["B"]),
        Course("B", "Course B", 3, "core"),
    ]
    order = topological_sort(courses, set())
    assert order == ["B", "A"]


def test_topological_sort_excludes_completed_courses():
    courses = [
        Course("A", "Course A", 3, "core", ["B"]),
        Course("B", "Course B", 3, "core"),
    ]
    order = topological_sort(courses, {"B"})
    assert order == ["A"]


def test_topological_sort_respects_branching_prerequisites():
    courses = [
        Course("A", "Course A", 3, "core", ["B", "C"]),
        Course("B", "Course B", 3, "core"),
        Course("C", "Course C", 3, "core"),
    ]
    order = topological_sort(courses, set())
    assert sorted(order) == ["A", "B", "C"]
    assert order.index("B") < order.index("A")
    assert order.index("C") < order.index("A")


def test_topological_sort_includes_disconnected_courses():
    courses = [
        Course("A", "Course A", 3, "core", ["B"]),
        Course("B", "Course B", 3, "core"),
        Course("C", "Course C", 3, "core"),
    ]
    order = topological_sort(courses, set())
    assert sorted(order) == ["A", "B", "C"]
    assert order.index("B") < order.index("A")


def test_topological_sort_rejects_cycles():
    courses = [
        Course("A", "Course A", 3, "core", ["B"]),
        Course("B", "Course B", 3, "core", ["A"]),
    ]
    with pytest.raises(ValueError, match="Cannot sort an invalid course graph"):
        topological_sort(courses, set())


def test_topological_sort_rejects_missing_prerequisites():
    courses = [
        Course("A", "Course A", 3, "core", ["B"]),
    ]
    with pytest.raises(ValueError, match="Cannot sort an invalid course graph"):
        topological_sort(courses, set())


def test_plan_multiple_semesters_separates_prerequisite_and_dependent():
    prerequisite = Course("B", "Course B", 3, "core")
    dependent = Course("A", "Course A", 3, "core", ["B"])
    courses = [dependent, prerequisite]
    semesters = plan_multiple_semesters(courses, set(), max_credits=6)
    assert semesters == [[prerequisite], [dependent]]


def test_plan_multiple_semesters_respects_credit_limit():
    first = Course("A", "Course A", 3, "core")
    second = Course("B", "Course B", 3, "core")
    semesters = plan_multiple_semesters([first, second], set(), max_credits=3)
    assert len(semesters) == 2
    assert [first] in semesters
    assert [second] in semesters


def test_plan_multiple_semesters_uses_and_preserves_completed_courses():
    prerequisite = Course("B", "Course B", 3, "core")
    dependent = Course("A", "Course A", 3, "core", ["B"])
    courses = [dependent, prerequisite]
    completed = {"B"}
    semesters = plan_multiple_semesters(courses, completed, max_credits=6)
    assert semesters == [[dependent]]
    assert completed == {"B"}


def test_plan_multiple_semesters_rejects_course_over_credit_limit():
    course = Course("A", "Course A", 4, "core")
    with pytest.raises(
        ValueError, match="Cannot schedule remaining courses within the credit limit"
    ):
        plan_multiple_semesters([course], set(), max_credits=3)


def test_plan_multiple_semesters_returns_empty_when_all_completed():
    course = Course("A", "Course A", 3, "core")
    completed = {"A"}
    semesters = plan_multiple_semesters([course], completed, max_credits=6)
    assert semesters == []


def test_plan_multiple_semesters_groups_independent_courses_when_they_fit():
    first = Course("A", "Course A", 3, "core")
    second = Course("B", "Course B", 3, "core")
    semesters = plan_multiple_semesters([first, second], set(), max_credits=6)
    assert len(semesters) == 1
    assert len(semesters[0]) == 2
    assert first in semesters[0]
    assert second in semesters[0]


@pytest.mark.parametrize("max_credits", [0, -1])
def test_plan_multiple_semesters_rejects_nonpositive_credit_limit(max_credits):
    course = Course("A", "Course A", 3, "core")
    with pytest.raises(ValueError, match="max_credits must be greater than 0"):
        plan_multiple_semesters([course], set(), max_credits=max_credits)


def test_plan_multiple_semesters_rejects_invalid_graph():
    courses = [
        Course("A", "Course A", 3, "core", ["B"]),
        Course("B", "Course B", 3, "core", ["A"]),
    ]
    with pytest.raises(ValueError, match="Cannot sort an invalid course graph"):
        plan_multiple_semesters(courses, set(), max_credits=6)
