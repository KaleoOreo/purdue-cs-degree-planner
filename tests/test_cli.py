from argparse import Namespace

from degree_planner.cli import build_parser, main, run_plan_command
from degree_planner.database import connect_database, mark_completed, save_course
from degree_planner.models import Course


def test_build_parser_uses_default_database_path():
    parser = build_parser()
    args = parser.parse_args(["plan"])

    assert args.database == "data/planner.db"


def test_main_accepts_database_argument():
    args = main(["--database", "data/test.db", "plan"])

    assert args.database == "data/test.db"


def test_plan_command_accepts_max_credits():
    args = main(["plan", "--max-credits", "12"])

    assert args.max_credits == 12


def test_run_plan_command_returns_course_codes():
    connection = connect_database("data/test_cli.db")
    save_course(connection, Course("CS 18000", "Problem Solving", 4, "core"))
    save_course(connection, Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]))
    mark_completed(connection, "CS 18000")

    result = run_plan_command(Namespace(database="data/test_cli.db", max_credits=15))

    assert result == ["CS 18200"]
