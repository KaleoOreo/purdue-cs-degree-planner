from degree_planner.models import Course


def find_missing_prerequisites(courses: list[Course]) -> list[tuple[str, str]]:
    course_codes = {course.code for course in courses}
    missing = []

    for course in courses:
        for prerequisite in course.prerequisites:
            if prerequisite not in course_codes:
                missing_pair = (course.code, prerequisite)
                if missing_pair not in missing:
                    missing.append(missing_pair)

    return missing


def has_cycle(courses: list[Course]) -> bool:
    course_by_code = {course.code: course for course in courses}

    for course in courses:
        for prerequisite in course.prerequisites:
            prerequisite_course = course_by_code.get(prerequisite)
            if prerequisite_course and course.code in prerequisite_course.prerequisites:
                return True

    return False
