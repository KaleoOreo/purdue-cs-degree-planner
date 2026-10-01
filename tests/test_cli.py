from argparse import Namespace
from pathlib import Path

import pytest

from degree_planner.cli import (
    build_parser,
    course_word,
    main,
    run_plan_command,
    run_validate_command,
)
from degree_planner.database import connect_database, load_courses, mark_completed, save_course
from degree_planner.models import Course

TEST_CLI_DATABASE = "data/test_cli.db"


def test_build_parser_uses_default_database_path():
    parser = build_parser()
    args = parser.parse_args(["plan"])

    assert args.database == "data/planner.db"


def test_main_accepts_database_argument():
    parser = build_parser()
    args = parser.parse_args(["--database", "data/test.db", "plan"])

    assert args.database == "data/test.db"


def test_plan_command_accepts_max_credits():
    parser = build_parser()
    args = parser.parse_args(["plan", "--max-credits", "12"])

    assert args.max_credits == 12


def test_import_command_accepts_csv_path():
    parser = build_parser()
    args = parser.parse_args(["import", "tests/fixtures/courses.csv"])

    assert args.csv_path == "tests/fixtures/courses.csv"


def test_complete_command_accepts_course_code():
    parser = build_parser()
    args = parser.parse_args(["complete", "CS 18000"])

    assert args.course_code == "CS 18000"


def test_courses_command_is_valid():
    parser = build_parser()
    args = parser.parse_args(["courses"])

    assert args.command == "courses"


def test_completed_command_is_valid():
    parser = build_parser()
    args = parser.parse_args(["completed"])

    assert args.command == "completed"


def test_validate_command_is_valid():
    parser = build_parser()
    args = parser.parse_args(["validate"])

    assert args.command == "validate"


def test_course_word_matches_count():
    assert course_word(1) == "course"
    assert course_word(2) == "courses"


def test_run_plan_command_returns_course_codes():
    Path(TEST_CLI_DATABASE).unlink(missing_ok=True)
    connection = connect_database(TEST_CLI_DATABASE)
    save_course(connection, Course("CS 18000", "Problem Solving", 4, "core"))
    save_course(connection, Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]))
    mark_completed(connection, "CS 18000")
    connection.close()

    result = run_plan_command(Namespace(database=TEST_CLI_DATABASE, max_credits=15))

    assert result == ["CS 18200"]


def test_run_plan_command_reports_when_no_courses_are_available():
    Path(TEST_CLI_DATABASE).unlink(missing_ok=True)
    connection = connect_database(TEST_CLI_DATABASE)
    connection.close()

    result = run_plan_command(Namespace(database=TEST_CLI_DATABASE, max_credits=15))

    assert result == ["No available courses"]


def test_main_runs_plan_command():
    Path(TEST_CLI_DATABASE).unlink(missing_ok=True)
    connection = connect_database(TEST_CLI_DATABASE)
    save_course(connection, Course("CS 18000", "Problem Solving", 4, "core"))
    connection.close()

    result = main(["--database", TEST_CLI_DATABASE, "plan"])

    assert result == ["CS 18000"]


def test_main_runs_import_command():
    Path(TEST_CLI_DATABASE).unlink(missing_ok=True)

    result = main([
        "--database", TEST_CLI_DATABASE,
        "import", "tests/fixtures/courses.csv",
    ])

    connection = connect_database(TEST_CLI_DATABASE)
    courses = load_courses(connection)
    connection.close()

    assert result == ["Imported 2 courses"]
    assert [course.code for course in courses] == ["CS 18000", "CS 18200"]


def test_main_reports_duplicate_import_error():
    Path(TEST_CLI_DATABASE).unlink(missing_ok=True)
    main(["--database", TEST_CLI_DATABASE, "import", "tests/fixtures/courses.csv"])

    result = main(["--database", TEST_CLI_DATABASE, "import", "tests/fixtures/courses.csv"])

    assert result == ["Error: duplicate course code during import"]


def test_main_runs_complete_command():
    Path(TEST_CLI_DATABASE).unlink(missing_ok=True)
    main(["--database", TEST_CLI_DATABASE, "import", "tests/fixtures/courses.csv"])

    result = main(["--database", TEST_CLI_DATABASE, "complete", "CS 18000"])
    plan = main(["--database", TEST_CLI_DATABASE, "plan"])

    assert result == ["Completed CS 18000"]
    assert plan == ["CS 18200"]


def test_main_runs_courses_command():
    Path(TEST_CLI_DATABASE).unlink(missing_ok=True)
    main(["--database", TEST_CLI_DATABASE, "import", "tests/fixtures/courses.csv"])

    result = main(["--database", TEST_CLI_DATABASE, "courses"])

    assert result == ["CS 18000", "CS 18200"]


def test_main_reports_when_no_courses_exist():
    Path(TEST_CLI_DATABASE).unlink(missing_ok=True)

    result = main(["--database", TEST_CLI_DATABASE, "courses"])

    assert result == ["No courses found"]


def test_main_runs_completed_command():
    Path(TEST_CLI_DATABASE).unlink(missing_ok=True)
    main(["--database", TEST_CLI_DATABASE, "complete", "CS 18000"])

    result = main(["--database", TEST_CLI_DATABASE, "completed"])

    assert result == ["CS 18000"]


def test_main_reports_when_no_completed_courses_exist():
    Path(TEST_CLI_DATABASE).unlink(missing_ok=True)

    result = main(["--database", TEST_CLI_DATABASE, "completed"])

    assert result == ["No completed courses"]


def test_run_validate_command_reports_valid_graph():
    Path(TEST_CLI_DATABASE).unlink(missing_ok=True)
    connection = connect_database(TEST_CLI_DATABASE)
    save_course(connection, Course("CS 18000", "Problem Solving", 4, "core"))
    save_course(connection, Course(
        "CS 18200", "Foundations", 3, "core", ["CS 18000"]
    ))
    connection.close()

    result = run_validate_command(Namespace(database=TEST_CLI_DATABASE))

    assert result == ["Course graph is valid"]


def test_run_validate_command_reports_grouped_problems():
    Path(TEST_CLI_DATABASE).unlink(missing_ok=True)
    connection = connect_database(TEST_CLI_DATABASE)
    save_course(connection, Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]))
    save_course(connection, Course("CS 24000", "Programming in C", 3, "core", ["CS 25100"]))
    save_course(connection, Course("CS 25100", "Data Structures", 3, "core", ["CS 24000"]))
    connection.close()

    result = run_validate_command(Namespace(database=TEST_CLI_DATABASE))

    assert result == [
        "Course graph is invalid",
        "Missing prerequisites:",
        "- CS 18200 requires CS 18000",
        "Cycle detected:",
        "- CS 24000 -> CS 25100 -> CS 24000",
    ]


def test_main_runs_validate_command():
    Path(TEST_CLI_DATABASE).unlink(missing_ok=True)

    result = main(["--database", TEST_CLI_DATABASE, "validate"])

    assert result == ["Course graph is valid"]


def test_main_runs_plan_all_command(tmp_path):
    database = str(tmp_path / "planner.db")
    main(["--database", database, "import", "tests/fixtures/courses.csv"])
    result = main(["--database", database, "plan-all", "--max-credits", "7"])
    assert result == [
        "Semester 1 (4 credits)",
        "  CS 18000: Problem Solving (4 credits)",
        "Semester 2 (3 credits)",
        "  CS 18200: Foundations (3 credits)",
    ]


def test_main_plan_all_reports_impossible_plan(tmp_path):
    database = str(tmp_path / "planner.db")
    main(["--database", database, "import", "tests/fixtures/courses.csv"])
    result = main(["--database", database, "plan-all", "--max-credits", "3"])
    assert result == [
        "Error: Cannot schedule remaining courses within the credit limit"
    ]


def test_main_plan_all_reports_empty_plan():
    result = main(["--database", ":memory:", "plan-all"])
    assert result == ["No remaining courses to plan"]


@pytest.mark.parametrize(
    "completed, expected",
    [
        pytest.param(
            {"CS 18000"},
            ["Example core: missing required courses", "  CS 18200"],
            id="partially-completed",
        ),
        pytest.param(
            {"CS 18000", "CS 18200"},
            ["Example core: no missing required courses"],
            id="all-completed",
        ),
    ],
)
def test_main_requirements_uses_saved_completions(tmp_path, completed, expected):
    database = str(tmp_path / "planner.db")
    requirements = tmp_path / "core.json"
    requirements.write_text(
        '{"name": "Example core", "course_codes": ["CS 18000", "CS 18200"]}',
        encoding="utf-8",
    )
    for code in completed:
        main(["--database", database, "complete", code])
    result = main(["--database", database, "requirements", str(requirements)])
    assert result == expected


@pytest.mark.parametrize(
    "completed, expected",
    [
        pytest.param(set(), ["Systems choice: 1 additional course required", "Remaining options:", "  CS 35200", "  CS 35400"], id="none-completed"),
        pytest.param({"CS 35400"}, ["Systems choice: satisfied"], id="choice-completed"),
    ],
)
def test_main_choice_requirements_uses_saved_completions(tmp_path, completed, expected):
    database = str(tmp_path / "planner.db")
    requirements = tmp_path / "choice.json"
    requirements.write_text(
        '{"name": "Systems choice", "course_codes": ["CS 35200", "CS 35400"], "required_count": 1}',
        encoding="utf-8",
    )
    for code in completed:
        main(["--database", database, "complete", code])
    result = main(["--database", database, "choice-requirements", str(requirements)])
    assert result == expected


@pytest.mark.parametrize(
    "completed, expected",
    [
        pytest.param({"A", "C"}, ["Example: incomplete", "Core: missing required courses", "  B", "Systems: satisfied"], id="incomplete"),
        pytest.param({"A", "B", "C"}, ["Example: complete", "Core: no missing required courses", "Systems: satisfied"], id="complete"),
    ],
)
def test_main_progress_uses_saved_completions(tmp_path, completed, expected):
    database = str(tmp_path / "planner.db")
    curriculum = tmp_path / "curriculum.json"
    curriculum.write_text(
        '{"name": "Example", "required_groups": [{"name": "Core", "course_codes": ["A", "B"]}], "choice_groups": [{"name": "Systems", "course_codes": ["C", "D"], "required_count": 1}]}',
        encoding="utf-8",
    )
    for code in completed:
        main(["--database", database, "complete", code])
    result = main(["--database", database, "progress", str(curriculum)])
    assert result == expected


def test_main_progress_reports_missing_curriculum_file(tmp_path):
    missing = tmp_path / "missing.json"
    result = main(["--database", ":memory:", "progress", str(missing)])
    assert result == [f"Error: Curriculum file not found: {missing}"]


def test_main_progress_reports_invalid_curriculum_file(tmp_path):
    curriculum = tmp_path / "invalid.json"
    curriculum.write_text('{"name": "Invalid"}', encoding="utf-8")
    result = main(["--database", ":memory:", "progress", str(curriculum)])
    assert result == ["Error: Missing required field: required_groups"]
