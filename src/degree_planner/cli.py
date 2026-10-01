import argparse

from degree_planner.database import (
    connect_database,
    load_completed_courses,
    load_courses,
    mark_completed,
)
from degree_planner.exceptions import DuplicateCourseError, RequirementsLoadError
from degree_planner.importers import (
    import_courses_from_csv,
    load_course_choice_group,
    load_required_course_group,
)
from degree_planner.reports import (
    course_codes,
    format_course_choice_group,
    format_required_course_group,
    format_semester_plan,
)
from degree_planner.services import (
    find_missing_required_courses_from_database,
    find_remaining_choice_count_from_database,
    find_remaining_choice_options_from_database,
    plan_multiple_semesters_from_database,
    plan_next_semester_from_database,
)
from degree_planner.validation import validate_course_graph


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
    plan_all_parser = subparsers.add_parser("plan-all")
    plan_all_parser.add_argument(
        "--max-credits",
        type=int,
        default=15,
    )
    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("csv_path")
    requirements_parser = subparsers.add_parser("requirements")
    requirements_parser.add_argument("requirements_path")
    choice_parser = subparsers.add_parser("choice-requirements")
    choice_parser.add_argument("requirements_path")
    complete_parser = subparsers.add_parser("complete")
    complete_parser.add_argument("course_code")
    subparsers.add_parser("courses")
    subparsers.add_parser("completed")
    subparsers.add_parser("validate")
    return parser


def main(argv: list[str] | None = None) -> list[str]:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "plan":
            return run_plan_command(args)

        if args.command == "plan-all":
            return run_plan_all_command(args)

        if args.command == "import":
            return run_import_command(args)

        if args.command == "requirements":
            return run_requirements_command(args)

        if args.command == "choice-requirements":
            return run_choice_requirements_command(args)

        if args.command == "complete":
            return run_complete_command(args)

        if args.command == "courses":
            return run_courses_command(args)

        if args.command == "completed":
            return run_completed_command(args)

        if args.command == "validate":
            return run_validate_command(args)
    except DuplicateCourseError as error:
        return [f"Error: {error}"]

    raise ValueError(f"unknown command: {args.command}")


def run_requirements_command(args: argparse.Namespace) -> list[str]:
    try:
        group = load_required_course_group(args.requirements_path)
    except FileNotFoundError:
        return [f"Error: Requirements file not found: {args.requirements_path}"]
    except RequirementsLoadError as error:
        return [f"Error: {error}"]
    connection = connect_database(args.database)
    try:
        missing = find_missing_required_courses_from_database(connection, group)
        return format_required_course_group(group.name, missing)
    finally:
        connection.close()


def run_choice_requirements_command(args: argparse.Namespace) -> list[str]:
    try:
        group = load_course_choice_group(args.requirements_path)
    except FileNotFoundError:
        return [f"Error: Requirements file not found: {args.requirements_path}"]
    except RequirementsLoadError as error:
        return [f"Error: {error}"]
    connection = connect_database(args.database)
    try:
        count = find_remaining_choice_count_from_database(connection, group)
        options = find_remaining_choice_options_from_database(connection, group)
        return format_course_choice_group(group.name, count, options)
    finally:
        connection.close()


def run_plan_command(args: argparse.Namespace) -> list[str]:
    connection = connect_database(args.database)
    try:
        plan = plan_next_semester_from_database(connection, args.max_credits)
        if not plan:
            return ["No available courses"]
        return course_codes(plan)
    finally:
        connection.close()


def run_plan_all_command(args: argparse.Namespace) -> list[str]:
    connection = connect_database(args.database)
    try:
        semesters = plan_multiple_semesters_from_database(connection, args.max_credits)
        return format_semester_plan(semesters)
    except ValueError as error:
        return [f"Error: {error}"]
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
        courses = load_courses(connection)
        if not courses:
            return ["No courses found"]
        return course_codes(courses)
    finally:
        connection.close()


def run_completed_command(args: argparse.Namespace) -> list[str]:
    connection = connect_database(args.database)
    try:
        completed = load_completed_courses(connection)
        if not completed:
            return ["No completed courses"]
        return sorted(completed)
    finally:
        connection.close()


def run_validate_command(args: argparse.Namespace) -> list[str]:
    connection = connect_database(args.database)
    try:
        courses = load_courses(connection)
        result = validate_course_graph(courses)
        if result.is_valid:
            return ["Course graph is valid"]

        messages = ["Course graph is invalid"]
        if result.missing_prerequisites:
            messages.append("Missing prerequisites:")
            for course_code, prerequisite_code in result.missing_prerequisites:
                messages.append(f"- {course_code} requires {prerequisite_code}")

        if result.cycle_path:
            messages.append("Cycle detected:")
            messages.append(f"- {' -> '.join(result.cycle_path)}")

        return messages
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
