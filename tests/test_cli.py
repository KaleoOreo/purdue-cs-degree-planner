from argparse import Namespace
from pathlib import Path

from degree_planner.cli import build_parser, course_word, main, run_plan_command
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
