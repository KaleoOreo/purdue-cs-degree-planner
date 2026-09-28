from dataclasses import dataclass


def find_missing_required_courses(
    required: set[str],
    completed: set[str],
) -> set[str]:
    return required - completed


@dataclass
class RequiredCourseGroup:
    name: str
    course_codes: set[str]

    def missing_courses(self, completed: set[str]) -> set[str]:
        return find_missing_required_courses(self.course_codes, completed)
