import pytest

from degree_planner.models import Course
from degree_planner.reports import (
    course_codes,
    format_course_choice_group,
    format_course_option_group,
    format_curriculum_progress,
    format_required_course_group,
    format_requirement_allocation,
    format_semester_plan,
    total_credits,
)
from degree_planner.requirements import (
    CourseChoiceGroup,
    CourseOption,
    CourseOptionGroup,
    Curriculum,
    CurriculumProgress,
    RequirementAllocation,
    RequiredCourseGroup,
)


def test_format_requirement_allocation_preserves_slots_and_sorts_pair():
    allocations = [
        RequirementAllocation("Systems", CourseOption(frozenset({"CS 35400"}))),
        RequirementAllocation(
            "Elective", CourseOption(frozenset({"CS 41100", "CS 31100"}))
        ),
    ]

    assert format_requirement_allocation(allocations) == [
        "Requirement allocation:",
        "  Systems: CS 35400",
        "  Elective: CS 31100 + CS 41100",
    ]


@pytest.mark.parametrize(
    "remaining_count, options, expected",
    [
        pytest.param(0, [], ["Elective: satisfied"], id="satisfied"),
        pytest.param(
            1,
            [CourseOption(frozenset({"B", "A"}))],
            ["Elective: 1 additional option required", "Remaining options:", "  A + B"],
            id="one-paired-option",
        ),
        pytest.param(
            2,
            [CourseOption(frozenset({"A"})), CourseOption(frozenset({"B"}))],
            ["Elective: 2 additional options required", "Remaining options:", "  A", "  B"],
            id="multiple-options",
        ),
    ],
)
def test_format_course_option_group(remaining_count, options, expected):
    assert format_course_option_group("Elective", remaining_count, options) == expected


@pytest.mark.parametrize(
    "completed, expected",
    [
        pytest.param({"A", "C"}, ["Example: incomplete", "Core: missing required courses", "  B", "Systems: satisfied"], id="incomplete"),
        pytest.param(
            {"A", "B", "C"},
            [
                "Example: complete",
                "Core: no missing required courses",
                "Systems: satisfied",
                "Requirement allocation:",
                "  Core: A",
                "  Core: B",
                "  Systems: C",
            ],
            id="complete",
        ),
    ],
)
def test_format_curriculum_progress(completed, expected):
    core = RequiredCourseGroup("Core", {"A", "B"})
    systems = CourseChoiceGroup("Systems", {"C", "D"}, 1)
    curriculum = Curriculum("Example", [core], [systems], [])
    progress = CurriculumProgress(curriculum, completed)
    assert format_curriculum_progress(progress) == expected


@pytest.mark.parametrize(
    "completed, expected",
    [
        pytest.param(
            {"E"},
            ["Example: incomplete", "Elective: 1 additional option required", "Remaining options:", "  D", "  E + F"],
            id="pair-partially-completed",
        ),
        pytest.param(
            {"E", "F"},
            ["Example: complete", "Elective: satisfied", "Requirement allocation:", "  Elective: E + F"],
            id="pair-completed",
        ),
    ],
)
def test_format_curriculum_progress_includes_option_groups(completed, expected):
    options = [CourseOption(frozenset({"D"})), CourseOption(frozenset({"E", "F"}))]
    elective = CourseOptionGroup("Elective", options, required_count=1)
    progress = CurriculumProgress(Curriculum("Example", [], [], [elective]), completed)

    assert format_curriculum_progress(progress) == expected


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
