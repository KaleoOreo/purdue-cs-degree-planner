from degree_planner.models import Course


def find_missing_prerequisites(courses: list[Course]) -> list[tuple[str, str]]:
    course_codes = {course.code for course in courses}
    missing = []

    for course in courses:
        for prerequisite in course.prerequisites:
            if prerequisite not in course_codes:
                missing.append((course.code, prerequisite))

    return missing
