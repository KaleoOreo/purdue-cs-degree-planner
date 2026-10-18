from pydantic import BaseModel


class CourseCompletionRequest(BaseModel):
    course_code: str


class CourseResponse(BaseModel):
    code: str
    title: str
    credits: int
    category: str
    prerequisites: list[str]


class MissingPrerequisiteResponse(BaseModel):
    course_code: str
    prerequisite_code: str


class ValidationResponse(BaseModel):
    is_valid: bool
    missing_prerequisites: list[MissingPrerequisiteResponse]
    cycle_path: list[str]
