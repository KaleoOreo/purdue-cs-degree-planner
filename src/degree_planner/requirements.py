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

    def remaining_options(self, completed: set[str]) -> set[str]:
        return self.course_codes - completed

    def is_satisfied(self, completed: set[str]) -> bool:
        return self.remaining_count(completed) == 0


@dataclass
class Curriculum:
    name: str
    required_groups: list[RequiredCourseGroup]
    choice_groups: list[CourseChoiceGroup]

    def is_satisfied(self, completed: set[str]) -> bool:
        return all(
            group.is_satisfied(completed) for group in self.required_groups
        ) and all(
            group.is_satisfied(completed) for group in self.choice_groups
        )


@dataclass
class CurriculumProgress:
    curriculum: Curriculum
    completed: set[str]

    @property
    def is_complete(self) -> bool:
        return self.curriculum.is_satisfied(self.completed)
