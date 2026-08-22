import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="degree-planner")
    parser.add_argument(
        "--database",
        default="data/planner.db",
    )
    return parser
