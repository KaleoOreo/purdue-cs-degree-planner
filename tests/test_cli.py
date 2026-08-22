from degree_planner.cli import build_parser, main


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
