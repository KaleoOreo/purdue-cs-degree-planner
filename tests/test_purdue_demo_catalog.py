from pathlib import Path

from degree_planner.importers import load_courses_from_csv
from degree_planner.planning import plan_multiple_semesters
from degree_planner.validation import validate_course_graph


CATALOG_PATH = Path(__file__).resolve().parents[1] / "data/purdue_cs_core_demo.csv"


def test_purdue_demo_catalog_has_valid_schedulable_prerequisites():
    courses = load_courses_from_csv(str(CATALOG_PATH))

    assert len(courses) == 8
    assert validate_course_graph(courses).is_valid
    semesters = plan_multiple_semesters(courses, completed=set(), max_credits=15)
    semester_by_code = {
        course.code: index
        for index, semester in enumerate(semesters)
        for course in semester
    }
    assert len(semester_by_code) == len(courses)
    for course in courses:
        for prerequisite in course.prerequisites:
            assert semester_by_code[prerequisite] < semester_by_code[course.code]
