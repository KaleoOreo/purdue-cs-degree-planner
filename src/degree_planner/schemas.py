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


class RequirementAllocationResponse(BaseModel):
    group_name: str
    course_codes: list[str]


class RequiredGroupProgressResponse(BaseModel):
    name: str
    course_codes: list[str]
    missing_course_codes: list[str]


class ChoiceGroupProgressResponse(BaseModel):
    name: str
    course_codes: list[str]
    required_count: int
    remaining_count: int
    remaining_course_codes: list[str]


class CourseOptionResponse(BaseModel):
    course_codes: list[str]


class OptionGroupProgressResponse(BaseModel):
    name: str
    options: list[CourseOptionResponse]
    required_count: int
    remaining_count: int
    remaining_options: list[CourseOptionResponse]


class CurriculumProgressResponse(BaseModel):
    name: str
    is_complete: bool
    completed_course_codes: list[str]
    required_groups: list[RequiredGroupProgressResponse]
    choice_groups: list[ChoiceGroupProgressResponse]
    option_groups: list[OptionGroupProgressResponse]
    allocations: list[RequirementAllocationResponse] | None
