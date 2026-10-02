from dataclasses import dataclass


@dataclass(frozen=True)
class CourseOption:
    course_codes: frozenset[str]

    def __post_init__(self) -> None:
        if not self.course_codes:
            raise ValueError("course option must include at least one course")

    def is_satisfied(self, completed: set[str]) -> bool:
        return self.course_codes <= completed

    def can_be_used(self, completed: set[str], used: set[str]) -> bool:
        return self.is_satisfied(completed) and self.course_codes.isdisjoint(used)


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


def _can_fill_requirement_slots(
    slots: list[list[CourseOption]],
    completed: set[str],
    slot_index: int = 0,
    used: set[str] | None = None,
) -> bool:
    if used is None:
        used = set()
    if slot_index == len(slots):
        return True
    for option in slots[slot_index]:
        if option.can_be_used(completed, used):
            next_used = used | option.course_codes
            if _can_fill_requirement_slots(slots, completed, slot_index + 1, next_used):
                return True
    return False


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
    option_groups: list[CourseOptionGroup]

    def is_satisfied(self, completed: set[str]) -> bool:
        return _can_fill_requirement_slots(
            build_requirement_slots(self),
            completed,
        )


def build_requirement_slots(curriculum: Curriculum) -> list[list[CourseOption]]:
    slots: list[list[CourseOption]] = []
    for group in curriculum.required_groups:
        for code in sorted(group.course_codes):
            slots.append([CourseOption(frozenset({code}))])
    for group in curriculum.choice_groups:
        options = [
            CourseOption(frozenset({code}))
            for code in sorted(group.course_codes)
        ]
        for _ in range(group.required_count):
            slots.append(options)
    for group in curriculum.option_groups:
        for _ in range(group.required_count):
            slots.append(group.options)
    return slots


@dataclass
class CurriculumProgress:
    curriculum: Curriculum
    completed: set[str]

    @property
    def is_complete(self) -> bool:
        return self.curriculum.is_satisfied(self.completed)
