import argparse

from degree_planner.database import (
    connect_database,
    load_completed_courses,
    load_courses,
    mark_completed,
)
from degree_planner.exceptions import DuplicateCourseError
from degree_planner.importers import import_courses_from_csv
from degree_planner.reports import course_codes
from degree_planner.services import plan_next_semester_from_database


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="degree-planner")
    parser.add_argument(
        "--database",
        default="data/planner.db",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan_parser = subparsers.add_parser("plan")
    plan_parser.add_argument(
        "--max-credits",
        type=int,
        default=15,
    )
    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("csv_path")
    complete_parser = subparsers.add_parser("complete")
    complete_parser.add_argument("course_code")
    subparsers.add_parser("courses")
    subparsers.add_parser("completed")
    return parser


def main(argv: list[str] | None = None) -> list[str]:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "plan":
            return run_plan_command(args)

        if args.command == "import":
            return run_import_command(args)

        if args.command == "complete":
            return run_complete_command(args)

        if args.command == "courses":
            return run_courses_command(args)

        if args.command == "completed":
            return run_completed_command(args)
    except DuplicateCourseError as error:
        return [f"Error: {error}"]

    raise ValueError(f"unknown command: {args.command}")


def run_plan_command(args: argparse.Namespace) -> list[str]:
    connection = connect_database(args.database)
    try:
        plan = plan_next_semester_from_database(connection, args.max_credits)
        if not plan:
            return ["No available courses"]
        return course_codes(plan)
    finally:
        connection.close()


def run_import_command(args: argparse.Namespace) -> list[str]:
    connection = connect_database(args.database)
    try:
        imported_count = import_courses_from_csv(connection, args.csv_path)
        return [f"Imported {imported_count} {course_word(imported_count)}"]
    finally:
        connection.close()


def run_complete_command(args: argparse.Namespace) -> list[str]:
    connection = connect_database(args.database)
    try:
        mark_completed(connection, args.course_code)
        return [f"Completed {args.course_code}"]
    finally:
        connection.close()


def run_courses_command(args: argparse.Namespace) -> list[str]:
    connection = connect_database(args.database)
    try:
        return course_codes(load_courses(connection))
    finally:
        connection.close()


def run_completed_command(args: argparse.Namespace) -> list[str]:
    connection = connect_database(args.database)
    try:
        return sorted(load_completed_courses(connection))
    finally:
        connection.close()


def course_word(count: int) -> str:
    if count == 1:
        return "course"
    return "courses"


def cli_entry() -> None:
    for code in main():
        print(code)


if __name__ == "__main__":
    cli_entry()
