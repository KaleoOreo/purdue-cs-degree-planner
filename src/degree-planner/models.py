from dataclasses import dataclass


@dataclass
class Course:
    code: str
    title: str
    credits: int
    catagory: str
