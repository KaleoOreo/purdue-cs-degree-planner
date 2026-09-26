from degree_planner.models import Course
from degree_planner.validation import validate_course_graph


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


def plan_next_semester(
    courses: list[Course],
    completed: set[str],
    max_credits: int,
) -> list[Course]:
    available = find_available_courses(courses, completed)
    return build_semester_plan(available, max_credits)


def build_dependents(courses: list[Course]) -> dict[str, list[str]]:
    dependents: dict[str, list[str]] = {}
    for course in courses:
        dependents[course.code] = []
    for course in courses:
        for prerequisite in course.prerequisites:
            dependents[prerequisite].append(course.code)
    return dependents


def count_unfinished_prerequisites(
    courses: list[Course],
    completed: set[str],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for course in courses:
        counts[course.code] = 0
        for prerequisite in course.prerequisites:
            if prerequisite not in completed:
                counts[course.code] += 1
    return counts


def topological_sort(
    courses: list[Course],
    completed: set[str],
) -> list[str]:
    validation = validate_course_graph(courses)
    if not validation.is_valid:
        raise ValueError("Cannot sort an invalid course graph")
    counts = count_unfinished_prerequisites(courses, completed)
    dependents = build_dependents(courses)
    ready: list[str] = []
    order: list[str] = []
    for course in courses:
        if course.code not in completed:
            if counts[course.code] == 0:
                ready.append(course.code)
    while ready:
        course_code = ready.pop()
        order.append(course_code)
        for dependent in dependents[course_code]:
            if dependent not in completed:
                counts[dependent] -= 1
                if counts[dependent] == 0:
                    ready.append(dependent)
    remaining_count = 0
    for course in courses:
        if course.code not in completed:
            remaining_count += 1
    if len(order) != remaining_count:
        raise ValueError("Cannot order all remaining courses")
    return order
