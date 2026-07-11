from degree_planner.models import Course


def find_available_courses(
    courses: list[Course],
    completed: set[str],
) -> list[Course]:
    return [
        course
        for course in courses
        if course.code not in completed
        and course.prerequisites_satisfied(completed)
    ]
