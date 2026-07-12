from degree_planner.models import Course


def course_codes(courses: list[Course]) -> list[str]:
    return [
        course.code
        for course in courses
    ]
