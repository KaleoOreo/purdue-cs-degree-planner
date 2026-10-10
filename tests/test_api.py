from degree_planner.api import app


def test_api_has_project_title():
    assert app.title == "Purdue CS Degree Planner API"
