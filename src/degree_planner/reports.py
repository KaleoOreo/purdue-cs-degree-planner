from degree_planner.models import Course


def course_codes(courses: list[Course]) -> list[str]:
    return [
        course.code
        for course in courses
    ]


def total_credits(courses: list[Course]) -> int:
    return sum(
        course.credits
        for course in courses
    )
