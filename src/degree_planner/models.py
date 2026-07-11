from dataclasses import dataclass, field


@dataclass
class Course:
    code: str
    title: str
    credits: int
    category: str
    prerequisites: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.credits <= 0:
            raise ValueError("credits must be greater than 0")

    def prerequisites_satisfied(self, completed: set[str]) -> bool:
        return all(
            prerequisite in completed
            for prerequisite in self.prerequisites
        )
