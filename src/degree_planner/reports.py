from degree_planner.models import Course
from degree_planner.requirements import CurriculumProgress


def format_course_choice_group(
    name: str,
    remaining_count: int,
    remaining_options: set[str],
) -> list[str]:
    if remaining_count == 0:
        return [f"{name}: satisfied"]
    course_word = "course" if remaining_count == 1 else "courses"
    lines = [f"{name}: {remaining_count} additional {course_word} required"]
    lines.append("Remaining options:")
    for code in sorted(remaining_options):
        lines.append(f"  {code}")
    return lines


def format_required_course_group(name: str, missing: set[str]) -> list[str]:
    if not missing:
        return [f"{name}: no missing required courses"]
    lines = [f"{name}: missing required courses"]
    for code in sorted(missing):
        lines.append(f"  {code}")
    return lines


def format_curriculum_progress(progress: CurriculumProgress) -> list[str]:
    status = "complete" if progress.is_complete else "incomplete"
    lines = [f"{progress.curriculum.name}: {status}"]
    for group in progress.curriculum.required_groups:
        missing = group.missing_courses(progress.completed)
        lines.extend(format_required_course_group(group.name, missing))
    for group in progress.curriculum.choice_groups:
        count = group.remaining_count(progress.completed)
        options = group.remaining_options(progress.completed)
        lines.extend(format_course_choice_group(group.name, count, options))
    return lines


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
