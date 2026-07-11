from dataclasses import dataclass


@dataclass
class Course:
    code: str
    title: str
    credits: int
    category: str

    def __post_init__(self) -> None:
        if self.credits <= 0:
            raise ValueError("credits must be greater than 0")
