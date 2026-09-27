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


def format_semester_plan(semesters: list[list[Course]]) -> list[str]:
    if not semesters:
        return ["No remaining courses to plan"]
    lines: list[str] = []
    for number, semester in enumerate(semesters, start=1):
        lines.append(f"Semester {number} ({total_credits(semester)} credits)")
        for course in semester:
            lines.append(
                f"  {course.code}: {course.title} ({course.credits} credits)"
            )
    return lines
