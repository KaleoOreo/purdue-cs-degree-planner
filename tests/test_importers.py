import sqlite3

import pytest

from degree_planner.database import initialize_database, load_courses
from degree_planner.exceptions import DuplicateCourseError, RequirementsLoadError
from degree_planner.importers import (
    course_from_row,
    import_courses_from_csv,
    load_course_choice_group,
    load_curriculum,
    load_courses_from_csv,
    load_required_course_group,
    parse_prerequisites,
)


def test_load_curriculum_from_json(tmp_path):
    path = tmp_path / "curriculum.json"
    path.write_text(
        '{"name": "Example curriculum", "required_groups": [{"name": "Core", "course_codes": ["A", "B"]}], "choice_groups": [{"name": "Systems", "course_codes": ["C", "D"], "required_count": 1}], "option_groups": [{"name": "Elective", "options": [["E"], ["F", "G"]], "required_count": 1}]}',
        encoding="utf-8",
    )
    curriculum = load_curriculum(str(path))
    assert curriculum.name == "Example curriculum"
    assert curriculum.required_groups[0].course_codes == {"A", "B"}
    assert curriculum.choice_groups[0].course_codes == {"C", "D"}
    assert curriculum.choice_groups[0].required_count == 1
    assert [option.course_codes for option in curriculum.option_groups[0].options] == [
        frozenset({"E"}), frozenset({"F", "G"})
    ]


def test_load_purdue_software_engineering_curriculum():
    curriculum = load_curriculum("data/purdue_software_engineering.json")
    assert curriculum.name == "Purdue CS - Software Engineering departmental requirements"
    assert curriculum.required_groups[0].course_codes == {
        "CS 18000", "CS 18200", "CS 24000", "CS 25000", "CS 25100", "CS 25200"
    }
    assert curriculum.required_groups[1].course_codes == {"CS 19300"}
    assert curriculum.required_groups[2].course_codes == {
        "CS 30700", "CS 38100", "CS 40700", "CS 40800"
    }
    assert curriculum.choice_groups[0].course_codes == {"CS 35200", "CS 35400"}
    assert curriculum.choice_groups[0].required_count == 1
    elective = curriculum.option_groups[0]
    assert elective.name == "Software Engineering elective"
    assert elective.required_count == 1
    assert {option.course_codes for option in elective.options} == {
        frozenset({"CS 31100", "CS 41100"}),
        frozenset({"CS 34800"}), frozenset({"CS 35100"}),
        frozenset({"CS 35200"}), frozenset({"CS 35300"}),
        frozenset({"CS 35400"}), frozenset({"CS 37300"}),
        frozenset({"CS 42200"}), frozenset({"CS 42600"}),
        frozenset({"CS 44800"}), frozenset({"CS 45600"}),
        frozenset({"CS 47300"}), frozenset({"CS 48900"}),
        frozenset({"CS 51000"}),
    }


@pytest.mark.parametrize(
    "additional_completions, expected",
    [
        pytest.param({"CS 35200"}, False, id="one-course-cannot-fill-two-slots"),
        pytest.param({"CS 35200", "CS 35400"}, True, id="overlap-courses-split"),
        pytest.param({"CS 35200", "CS 31100"}, False, id="paired-option-incomplete"),
        pytest.param(
            {"CS 35200", "CS 31100", "CS 41100"},
            True,
            id="paired-option-complete",
        ),
    ],
)
def test_purdue_curriculum_allocates_track_options(additional_completions, expected):
    curriculum = load_curriculum("data/purdue_software_engineering.json")
    completed: set[str] = set()
    for group in curriculum.required_groups:
        completed.update(group.course_codes)
    completed.update(additional_completions)

    assert curriculum.is_satisfied(completed) is expected


@pytest.mark.parametrize(
    "content, message",
    [
        pytest.param('{"required_groups": [], "choice_groups": [], "option_groups": []}', "Missing required field: name", id="missing-name"),
        pytest.param('{"name": "Example", "choice_groups": [], "option_groups": []}', "Missing required field: required_groups", id="missing-required-groups"),
        pytest.param('{"name": "Example", "required_groups": [], "choice_groups": []}', "Missing required field: option_groups", id="missing-option-groups"),
        pytest.param('{"name": 42, "required_groups": [], "choice_groups": [], "option_groups": []}', "Field 'name' must be a string", id="name-not-string"),
        pytest.param('{"name": "Example", "required_groups": {}, "choice_groups": [], "option_groups": []}', "Field 'required_groups' must be a list", id="required-groups-not-list"),
        pytest.param('{"name": "Example", "required_groups": [], "choice_groups": {}, "option_groups": []}', "Field 'choice_groups' must be a list", id="choice-groups-not-list"),
        pytest.param('{"name": "Example", "required_groups": [], "choice_groups": [], "option_groups": {}}', "Field 'option_groups' must be a list", id="option-groups-not-list"),
    ],
)
def test_load_curriculum_rejects_invalid_outer_data(tmp_path, content, message):
    path = tmp_path / "curriculum.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(RequirementsLoadError, match=message):
        load_curriculum(str(path))


@pytest.mark.parametrize(
    "content, message",
    [
        pytest.param('{"name": "Example", "required_groups": [{"name": "Core"}], "choice_groups": [], "option_groups": []}', "Missing required field: course_codes", id="invalid-required-group"),
        pytest.param('{"name": "Example", "required_groups": [], "choice_groups": [{"name": "Systems", "course_codes": ["C", "D"]}], "option_groups": []}', "Missing required field: required_count", id="choice-count-missing"),
        pytest.param('{"name": "Example", "required_groups": [], "choice_groups": [{"name": "Systems", "course_codes": ["C", "D"], "required_count": 3}], "option_groups": []}', "must be between 1", id="choice-count-too-large"),
        pytest.param('{"name": "Example", "required_groups": [], "choice_groups": [], "option_groups": [{"name": "Elective", "required_count": 1}]}', "Missing required field: options", id="option-list-missing"),
        pytest.param('{"name": "Example", "required_groups": [], "choice_groups": [], "option_groups": [{"name": "Elective", "options": ["A"], "required_count": 1}]}', "Each course option must be a list", id="option-not-list"),
        pytest.param('{"name": "Example", "required_groups": [], "choice_groups": [], "option_groups": [{"name": "Elective", "options": [["A", "A"]], "required_count": 1}]}', "duplicate course codes", id="duplicate-code-in-option"),
        pytest.param('{"name": "Example", "required_groups": [], "choice_groups": [], "option_groups": [{"name": "Elective", "options": [[]], "required_count": 1}]}', "must include at least one course", id="empty-option"),
        pytest.param('{"name": "Example", "required_groups": [], "choice_groups": [], "option_groups": [{"name": "Elective", "options": [["A", "B"], ["B", "C"]], "required_count": 1}]}', "overlapping courses", id="overlapping-options"),
    ],
)
def test_load_curriculum_rejects_invalid_nested_groups(tmp_path, content, message):
    path = tmp_path / "curriculum.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(RequirementsLoadError, match=message):
        load_curriculum(str(path))


def test_load_course_choice_group_from_json(tmp_path):
    path = tmp_path / "choice.json"
    path.write_text(
        '{"name": "Systems choice", "course_codes": ["CS 35200", "CS 35400"], "required_count": 1}',
        encoding="utf-8",
    )
    group = load_course_choice_group(str(path))
    assert group.name == "Systems choice"
    assert group.course_codes == {"CS 35200", "CS 35400"}
    assert group.required_count == 1
    assert group.remaining_count({"CS 35200"}) == 0


@pytest.mark.parametrize(
    "content, message",
    [
        pytest.param('{"name": "Choice", "course_codes": ["A", "B"]}', "Missing required field: required_count", id="missing-count"),
        pytest.param('{"name": "Choice", "course_codes": ["A", "B"], "required_count": "one"}', "must be an integer", id="count-not-integer"),
        pytest.param('{"name": "Choice", "course_codes": ["A", "B"], "required_count": 0}', "must be between 1", id="zero-count"),
        pytest.param('{"name": "Choice", "course_codes": ["A", "B"], "required_count": 3}', "must be between 1", id="count-exceeds-choices"),
    ],
)
def test_load_course_choice_group_rejects_invalid_count(tmp_path, content, message):
    path = tmp_path / "choice.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(RequirementsLoadError, match=message):
        load_course_choice_group(str(path))


def test_load_required_course_group_from_json(tmp_path):
    path = tmp_path / "core.json"
    path.write_text(
        '{"name": "Example core", "course_codes": ["CS 18000", "CS 18200"]}',
        encoding="utf-8",
    )
    group = load_required_course_group(str(path))
    assert group.name == "Example core"
    assert group.course_codes == {"CS 18000", "CS 18200"}


@pytest.mark.parametrize(
    "content, message",
    [
        pytest.param('[]', "must contain an object", id="not-an-object"),
        pytest.param('{"course_codes": []}', "Missing required field: name", id="missing-name"),
        pytest.param('{"name": "Core"}', "Missing required field: course_codes", id="missing-codes"),
        pytest.param(
            '{"name": 42, "course_codes": []}', "Field 'name' must be a string", id="name-not-string",
        ),
        pytest.param(
            '{"name": "Core", "course_codes": 42}', "Field 'course_codes' must be a list", id="codes-number",
        ),
        pytest.param(
            '{"name": "Core", "course_codes": "CS 18000"}', "Field 'course_codes' must be a list", id="codes-string",
        ),
        pytest.param(
            '{"name": "Core", "course_codes": ["CS 18000", 42]}', "Every course code must be a string", id="code-not-string",
        ),
    ],
)
def test_load_required_course_group_rejects_invalid_data(tmp_path, content, message):
    path = tmp_path / "requirements.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(RequirementsLoadError, match=message):
        load_required_course_group(str(path))


def test_parse_prerequisites_splits_semicolon_values():
    assert parse_prerequisites("CS 18000;CS 18200") == ["CS 18000", "CS 18200"]


def test_parse_prerequisites_returns_empty_list_for_empty_value():
    assert parse_prerequisites("") == []


def test_parse_prerequisites_returns_empty_list_for_spaces():
    assert parse_prerequisites("   ") == []


def test_parse_prerequisites_ignores_blank_parts():
    assert parse_prerequisites("CS 18000; ") == ["CS 18000"]


def test_course_from_row_converts_csv_row_to_course():
    row = {
        "code": "CS 24000",
        "title": "Programming in C",
        "credits": "3",
        "category": "core",
        "prerequisites": "CS 18000;CS 18200",
    }

    course = course_from_row(row)

    assert course.code == "CS 24000"
    assert course.credits == 3
    assert course.prerequisites == ["CS 18000", "CS 18200"]


def test_load_courses_from_csv_returns_courses():
    courses = load_courses_from_csv("tests/fixtures/courses.csv")

    assert [course.code for course in courses] == ["CS 18000", "CS 18200"]
    assert courses[1].prerequisites == ["CS 18000"]


def test_import_courses_from_csv_saves_courses_to_database():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    imported_count = import_courses_from_csv(connection, "tests/fixtures/courses.csv")
    courses = load_courses(connection)

    assert imported_count == 2
    assert [course.code for course in courses] == ["CS 18000", "CS 18200"]
    assert courses[1].prerequisites == ["CS 18000"]


def test_import_courses_from_csv_rejects_duplicate_course_codes():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    import_courses_from_csv(connection, "tests/fixtures/courses.csv")

    with pytest.raises(DuplicateCourseError):
        import_courses_from_csv(connection, "tests/fixtures/courses.csv")
