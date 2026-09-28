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

    def is_satisfied(self, completed: set[str]) -> bool:
        return not self.missing_courses(completed)


@dataclass
class CourseChoiceGroup:
    name: str
    course_codes: set[str]
    required_count: int

    def __post_init__(self) -> None:
        if not 1 <= self.required_count <= len(self.course_codes):
            raise ValueError("required_count must be between 1 and the number of choices")

    def remaining_count(self, completed: set[str]) -> int:
        qualifying = self.course_codes & completed
        return max(0, self.required_count - len(qualifying))
