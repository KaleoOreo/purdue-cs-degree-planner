import argparse

from degree_planner.database import connect_database
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
    return parser


def main(argv: list[str] | None = None) -> list[str]:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "plan":
        return run_plan_command(args)

    if args.command == "import":
        return run_import_command(args)

    raise ValueError(f"unknown command: {args.command}")


def run_plan_command(args: argparse.Namespace) -> list[str]:
    connection = connect_database(args.database)
    try:
        plan = plan_next_semester_from_database(connection, args.max_credits)
        return course_codes(plan)
    finally:
        connection.close()


def run_import_command(args: argparse.Namespace) -> list[str]:
    connection = connect_database(args.database)
    try:
        import_courses_from_csv(connection, args.csv_path)
        return []
    finally:
        connection.close()


def cli_entry() -> None:
    for code in main():
        print(code)


if __name__ == "__main__":
    cli_entry()
