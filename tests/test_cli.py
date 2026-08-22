from degree_planner.cli import build_parser, main


def test_build_parser_uses_default_database_path():
    parser = build_parser()
    args = parser.parse_args([])

    assert args.database == "data/planner.db"


def test_main_accepts_database_argument():
    args = main(["--database", "data/test.db"])

    assert args.database == "data/test.db"
