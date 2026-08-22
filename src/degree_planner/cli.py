import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="degree-planner")
    parser.add_argument(
        "--database",
        default="data/planner.db",
    )
    return parser


def main(argv: list[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    return parser.parse_args(argv)
