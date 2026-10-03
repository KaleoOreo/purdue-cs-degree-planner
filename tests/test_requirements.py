import pytest

from degree_planner.requirements import (
    _can_fill_requirement_slots,
    _find_requirement_slot_allocation,
    CourseChoiceGroup,
    CourseOption,
    CourseOptionGroup,
    Curriculum,
    RequirementAllocation,
    RequirementSlot,
    RequiredCourseGroup,
    build_requirement_slots,
    find_missing_required_courses,
)


def test_requirement_allocation_returns_choices_after_backtracking():
    slots = [
        RequirementSlot("First", (
            CourseOption(frozenset({"A"})), CourseOption(frozenset({"B"}))
        )),
        RequirementSlot("Second", (CourseOption(frozenset({"A"})),)),
    ]

    allocation = _find_requirement_slot_allocation(slots, {"A", "B"})

    assert allocation == [
        CourseOption(frozenset({"B"})),
        CourseOption(frozenset({"A"})),
    ]


def test_requirement_allocation_returns_none_when_no_path_works():
    shared_option = CourseOption(frozenset({"A"}))
    slots = [
        RequirementSlot("First", (shared_option,)),
        RequirementSlot("Second", (shared_option,)),
    ]

    assert _find_requirement_slot_allocation(slots, {"A"}) is None


def test_requirement_allocation_returns_empty_list_for_no_slots():
    assert _find_requirement_slot_allocation([], set()) == []


def test_requirement_slots_backtrack_after_first_choice_fails():
    slots = [
        RequirementSlot("First", (
            CourseOption(frozenset({"A"})), CourseOption(frozenset({"B"}))
        )),
        RequirementSlot("Second", (CourseOption(frozenset({"A"})),)),
    ]

    result = _can_fill_requirement_slots(slots, completed={"A", "B"})

    assert result is True


def test_requirement_slots_do_not_count_one_course_twice():
    shared_option = CourseOption(frozenset({"A"}))
    slots = [
        RequirementSlot("First", (shared_option,)),
        RequirementSlot("Second", (shared_option,)),
    ]

    result = _can_fill_requirement_slots(slots, completed={"A"})

    assert result is False


@pytest.mark.parametrize(
    "completed, expected",
    [
        pytest.param({"A"}, False, id="half-pair-completed"),
        pytest.param({"A", "B"}, True, id="whole-pair-completed"),
    ],
)
def test_requirement_slots_treat_paired_courses_as_one_option(completed, expected):
    slots = [
        RequirementSlot("Pair", (CourseOption(frozenset({"A", "B"})),))
    ]

    assert _can_fill_requirement_slots(slots, completed) is expected


def test_build_requirement_slots_normalizes_every_group_type():
    curriculum = Curriculum(
        "Example",
        [RequiredCourseGroup("Core", {"A"})],
        [CourseChoiceGroup("Choose two", {"B", "C", "D"}, 2)],
        [CourseOptionGroup("Elective", [CourseOption(frozenset({"E", "F"}))], 1)],
    )

    slots = build_requirement_slots(curriculum)

    assert [slot.group_name for slot in slots] == [
        "Core", "Choose two", "Choose two", "Elective"
    ]
    assert [[option.course_codes for option in slot.options] for slot in slots] == [
        [frozenset({"A"})],
        [frozenset({"B"}), frozenset({"C"}), frozenset({"D"})],
        [frozenset({"B"}), frozenset({"C"}), frozenset({"D"})],
        [frozenset({"E", "F"})],
    ]


@pytest.mark.parametrize(
    "course_codes, completed, expected",
    [
        pytest.param({"A"}, {"A"}, True, id="single-course-completed"),
        pytest.param({"A", "B"}, {"A"}, False, id="pair-partially-completed"),
        pytest.param({"A", "B"}, {"A", "B", "X"}, True, id="pair-completed"),
    ],
)
def test_course_option_requires_every_course(course_codes, completed, expected):
    option = CourseOption(frozenset(course_codes))
    assert option.is_satisfied(completed) is expected


@pytest.mark.parametrize(
    "completed, used, expected",
    [
        pytest.param({"A", "B"}, set(), True, id="completed-and-unused"),
        pytest.param({"A"}, set(), False, id="partially-completed"),
        pytest.param({"A", "B"}, {"A"}, False, id="one-course-already-used"),
    ],
)
def test_course_option_can_only_use_completed_unallocated_courses(
    completed, used, expected
):
    option = CourseOption(frozenset({"A", "B"}))
    assert option.can_be_used(completed, used) is expected


def test_course_option_rejects_empty_course_set():
    with pytest.raises(ValueError, match="must include at least one course"):
        CourseOption(frozenset())


@pytest.mark.parametrize(
    "completed, expected",
    [
        pytest.param(set(), 1, id="nothing-completed"),
        pytest.param({"B"}, 1, id="half-pair-completed"),
        pytest.param({"B", "C"}, 0, id="pair-completed"),
        pytest.param({"A"}, 0, id="single-option-completed"),
        pytest.param({"A", "B", "C"}, 0, id="extra-option-completed"),
    ],
)
def test_course_option_group_counts_completed_options(completed, expected):
    options = [CourseOption(frozenset({"A"})), CourseOption(frozenset({"B", "C"}))]
    group = CourseOptionGroup("Example elective", options, required_count=1)
    assert group.remaining_count(completed) == expected


@pytest.mark.parametrize(
    "options, required_count",
    [
        pytest.param([CourseOption(frozenset({"A"}))], 0, id="zero-required"),
        pytest.param([CourseOption(frozenset({"A"}))], -1, id="negative-required"),
        pytest.param([CourseOption(frozenset({"A"}))], 2, id="too-many-required"),
        pytest.param([], 1, id="no-options"),
    ],
)
def test_course_option_group_rejects_invalid_counts(options, required_count):
    with pytest.raises(ValueError, match="required_count must be between"):
        CourseOptionGroup("Example elective", options, required_count)


@pytest.mark.parametrize(
    "options, message",
    [
        pytest.param(
            [CourseOption(frozenset({"A"})), CourseOption(frozenset({"A"}))],
            "duplicate options",
            id="duplicate-options",
        ),
        pytest.param(
            [CourseOption(frozenset({"A", "B"})), CourseOption(frozenset({"B", "C"}))],
            "overlapping courses",
            id="overlapping-options",
        ),
    ],
)
def test_course_option_group_rejects_reused_options(options, message):
    with pytest.raises(ValueError, match=message):
        CourseOptionGroup("Example elective", options, required_count=1)


@pytest.mark.parametrize(
    "completed, expected_options, expected_satisfied",
    [
        pytest.param({"B"}, [{"A"}, {"B", "C"}], False, id="pair-partial"),
        pytest.param({"A"}, [{"B", "C"}], True, id="single-option-complete"),
        pytest.param({"B", "C"}, [{"A"}], True, id="paired-option-complete"),
    ],
)
def test_course_option_group_reports_remaining_options(
    completed, expected_options, expected_satisfied
):
    options = [CourseOption(frozenset({"A"})), CourseOption(frozenset({"B", "C"}))]
    group = CourseOptionGroup("Example elective", options, required_count=1)
    remaining = [option.course_codes for option in group.remaining_options(completed)]
    assert remaining == [frozenset(codes) for codes in expected_options]
    assert group.is_satisfied(completed) is expected_satisfied


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


def test_curriculum_keeps_requirement_groups_separate():
    core = RequiredCourseGroup("Core", {"A", "B"})
    systems = CourseChoiceGroup("Systems", {"C", "D"}, 1)
    curriculum = Curriculum("Example curriculum", [core], [systems], [])

    assert curriculum.name == "Example curriculum"
    assert curriculum.required_groups == [core]
    assert curriculum.choice_groups == [systems]


@pytest.mark.parametrize(
    "completed, expected",
    [
        pytest.param({"A", "B", "C"}, True, id="all-groups-satisfied"),
        pytest.param({"A", "C"}, False, id="required-group-incomplete"),
        pytest.param({"A", "B"}, False, id="choice-group-incomplete"),
    ],
)
def test_curriculum_requires_every_group_to_be_satisfied(completed, expected):
    core = RequiredCourseGroup("Core", {"A", "B"})
    systems = CourseChoiceGroup("Systems", {"C", "D"}, 1)
    curriculum = Curriculum("Example curriculum", [core], [systems], [])

    assert curriculum.is_satisfied(completed) is expected


@pytest.mark.parametrize(
    "completed, expected",
    [
        pytest.param({"A"}, False, id="shared-course-cannot-fill-both-groups"),
        pytest.param({"A", "B"}, True, id="separate-course-fills-choice-group"),
    ],
)
def test_curriculum_does_not_count_a_course_for_two_groups(completed, expected):
    required = RequiredCourseGroup("Required", {"A"})
    choice = CourseChoiceGroup("Choice", {"A", "B"}, 1)
    curriculum = Curriculum("Example", [required], [choice], [])

    assert curriculum.is_satisfied(completed) is expected


def test_curriculum_finds_allocation_across_overlapping_groups():
    required = RequiredCourseGroup("Required", {"A"})
    choice = CourseChoiceGroup("Choice", {"A", "B"}, 1)
    curriculum = Curriculum("Example", [required], [choice], [])

    assert curriculum.find_allocation({"A"}) is None
    assert curriculum.find_allocation({"A", "B"}) == [
        RequirementAllocation("Required", CourseOption(frozenset({"A"}))),
        RequirementAllocation("Choice", CourseOption(frozenset({"B"}))),
    ]


def test_empty_curriculum_is_satisfied():
    curriculum = Curriculum("Empty", [], [], [])

    assert curriculum.is_satisfied(set()) is True


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


@pytest.mark.parametrize(
    "completed, expected",
    [
        pytest.param(set(), {"A", "B", "C"}, id="none-completed"),
        pytest.param({"A", "X"}, {"B", "C"}, id="one-option-completed"),
        pytest.param({"A", "B", "C"}, set(), id="all-options-completed"),
    ],
)
def test_course_choice_group_returns_remaining_options(completed, expected):
    group = CourseChoiceGroup("Example elective", {"A", "B", "C"}, 2)
    assert group.remaining_options(completed) == expected


@pytest.mark.parametrize(
    "course_codes, required_count",
    [
        pytest.param({"A", "B", "C"}, 0, id="zero-required"),
        pytest.param({"A", "B", "C"}, -1, id="negative-required"),
        pytest.param({"A", "B", "C"}, 4, id="too-many-required"),
        pytest.param(set(), 1, id="no-choices"),
    ],
)
def test_course_choice_group_rejects_invalid_counts(course_codes, required_count):
    with pytest.raises(ValueError, match="required_count must be between"):
        CourseChoiceGroup("Example elective", course_codes, required_count)


@pytest.mark.parametrize(
    "completed, expected",
    [
        pytest.param({"A", "X"}, False, id="not-enough"),
        pytest.param({"A", "C"}, True, id="exactly-enough"),
        pytest.param({"A", "B", "C"}, True, id="extra-completions"),
    ],
)
def test_course_choice_group_reports_satisfaction(completed, expected):
    group = CourseChoiceGroup("Example elective", {"A", "B", "C"}, 2)
    assert group.is_satisfied(completed) is expected
