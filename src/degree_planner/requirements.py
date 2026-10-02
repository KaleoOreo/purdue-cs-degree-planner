from dataclasses import dataclass


@dataclass(frozen=True)
class CourseOption:
    course_codes: frozenset[str]

    def __post_init__(self) -> None:
        if not self.course_codes:
            raise ValueError("course option must include at least one course")

    def is_satisfied(self, completed: set[str]) -> bool:
        return self.course_codes <= completed


@dataclass
class CourseOptionGroup:
    name: str
    options: list[CourseOption]
    required_count: int

    def __post_init__(self) -> None:
        if not 1 <= self.required_count <= len(self.options):
            raise ValueError("required_count must be between 1 and the number of options")
        if len(set(self.options)) != len(self.options):
            raise ValueError("course option group cannot contain duplicate options")
        seen_courses: set[str] = set()
        for option in self.options:
            if seen_courses & option.course_codes:
                raise ValueError("course options cannot contain overlapping courses")
            seen_courses.update(option.course_codes)

    def remaining_count(self, completed: set[str]) -> int:
        satisfied_count = sum(
            option.is_satisfied(completed) for option in self.options
        )
        return max(0, self.required_count - satisfied_count)

    def remaining_options(self, completed: set[str]) -> list[CourseOption]:
        return [
            option for option in self.options if not option.is_satisfied(completed)
        ]

    def is_satisfied(self, completed: set[str]) -> bool:
        return self.remaining_count(completed) == 0


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
