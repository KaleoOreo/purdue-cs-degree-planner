from degree_planner.cli import build_parser


def test_build_parser_uses_default_database_path():
    parser = build_parser()
    args = parser.parse_args([])

    assert args.database == "data/planner.db"
