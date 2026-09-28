from degree_planner.requirements import find_missing_required_courses


def test_find_missing_required_courses_ignores_unrelated_completions():
    required = {"CS 18000", "CS 18200", "CS 24000"}
    completed = {"CS 18000", "CS 18200", "OTHER 10000"}
    missing = find_missing_required_courses(required, completed)
    assert missing == {"CS 24000"}
