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


def find_two_course_cycles(courses: list[Course]) -> list[tuple[str, str]]:
    course_by_code = {course.code: course for course in courses}
    cycles = []

    for course in courses:
        for prerequisite in course.prerequisites:
            prerequisite_course = course_by_code.get(prerequisite)
            if prerequisite_course and course.code in prerequisite_course.prerequisites:
                cycle = (course.code, prerequisite)
                reverse_cycle = (prerequisite, course.code)
                if cycle not in cycles and reverse_cycle not in cycles:
                    cycles.append(cycle)

    return cycles


def has_cycle(courses: list[Course]) -> bool:
    course_by_code = {course.code: course for course in courses}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(course_code: str) -> bool:
        if course_code in visiting:
            return True
        if course_code in visited:
            return False

        visiting.add(course_code)
        course = course_by_code[course_code]

        for prerequisite in course.prerequisites:
            if prerequisite not in course_by_code:
                continue
            if visit(prerequisite):
                return True

        visiting.remove(course_code)
        visited.add(course_code)
        return False

    for course in courses:
        if visit(course.code):
            return True

    return False
