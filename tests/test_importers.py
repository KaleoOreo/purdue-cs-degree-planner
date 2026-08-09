from degree_planner.importers import parse_prerequisites


def test_parse_prerequisites_splits_semicolon_values():
    assert parse_prerequisites("CS 18000;CS 18200") == ["CS 18000", "CS 18200"]


def test_parse_prerequisites_returns_empty_list_for_empty_value():
    assert parse_prerequisites("") == []
