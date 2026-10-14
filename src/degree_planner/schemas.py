from pydantic import BaseModel


class CourseResponse(BaseModel):
    code: str
    title: str
    credits: int
    category: str
    prerequisites: list[str]
