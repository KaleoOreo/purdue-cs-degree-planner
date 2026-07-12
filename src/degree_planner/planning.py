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


def build_semester_plan(
    available_courses: list[Course],
    max_credits: int,
) -> list[Course]:
    if max_credits <= 0:
        raise ValueError("max_credits must be greater than 0")

    plan: list[Course] = []
    total_credits = 0

    for course in available_courses:
        if total_credits + course.credits <= max_credits:
            plan.append(course)
            total_credits += course.credits

    return plan
