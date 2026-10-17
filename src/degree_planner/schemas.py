from pydantic import BaseModel


class CourseCompletionRequest(BaseModel):
    course_code: str


class CourseResponse(BaseModel):
    code: str
    title: str
    credits: int
    category: str
    prerequisites: list[str]
