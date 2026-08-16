from degree_planner.importers import course_from_row, parse_prerequisites


def test_parse_prerequisites_splits_semicolon_values():
    assert parse_prerequisites("CS 18000;CS 18200") == ["CS 18000", "CS 18200"]


def test_parse_prerequisites_returns_empty_list_for_empty_value():
    assert parse_prerequisites("") == []


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
