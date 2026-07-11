from degree_planner.models import Course


def test_course_stores_basic_fields():
    course = Course("CS 18000", "Problem Solving", 4, "core")

    assert course.code == "CS 18000"
    assert course.credits == 4
