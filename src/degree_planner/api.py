import sqlite3
from collections.abc import Iterator

from fastapi import Depends, FastAPI, HTTPException, Query

from degree_planner.database import (
    connect_database,
    load_completed_courses,
    load_courses,
)
from degree_planner.exceptions import CourseNotFoundError
from degree_planner.models import Course
from degree_planner.requirements import (
    CourseChoiceGroup,
    CourseOption,
    CourseOptionGroup,
    Curriculum,
    CurriculumProgress,
    RequirementAllocation,
    RequiredCourseGroup,
)
from degree_planner.schemas import (
    ChoiceGroupProgressResponse,
    CourseCompletionRequest,
    CourseOptionResponse,
    CourseResponse,
    CurriculumProgressResponse,
    MissingPrerequisiteResponse,
    OptionGroupProgressResponse,
    RequirementAllocationResponse,
    RequiredGroupProgressResponse,
    ValidationResponse,
)
from degree_planner.services import (
    mark_course_completed_from_database,
    plan_multiple_semesters_from_database,
    plan_next_semester_from_database,
)
from degree_planner.validation import validate_course_graph


DATABASE_PATH = "data/planner.db"


app = FastAPI(title="Purdue CS Degree Planner API")


def get_database() -> Iterator[sqlite3.Connection]:
    connection = connect_database(DATABASE_PATH)
    try:
        yield connection
    finally:
        connection.close()


def _required_group_progress_response(
    group: RequiredCourseGroup,
    completed: set[str],
) -> RequiredGroupProgressResponse:
    return RequiredGroupProgressResponse(
        name=group.name,
        course_codes=sorted(group.course_codes),
        missing_course_codes=sorted(group.missing_courses(completed)),
    )


def _choice_group_progress_response(
    group: CourseChoiceGroup,
    completed: set[str],
) -> ChoiceGroupProgressResponse:
    return ChoiceGroupProgressResponse(
        name=group.name,
        course_codes=sorted(group.course_codes),
        required_count=group.required_count,
        remaining_count=group.remaining_count(completed),
        remaining_course_codes=sorted(group.remaining_options(completed)),
    )


def _course_option_response(option: CourseOption) -> CourseOptionResponse:
    return CourseOptionResponse(course_codes=sorted(option.course_codes))


def _option_group_progress_response(
    group: CourseOptionGroup,
    completed: set[str],
) -> OptionGroupProgressResponse:
    return OptionGroupProgressResponse(
        name=group.name,
        options=[_course_option_response(option) for option in group.options],
        required_count=group.required_count,
        remaining_count=group.remaining_count(completed),
        remaining_options=[
            _course_option_response(option)
            for option in group.remaining_options(completed)
        ],
    )


def _requirement_allocation_response(
    allocation: RequirementAllocation,
) -> RequirementAllocationResponse:
    option = _course_option_response(allocation.option)
    return RequirementAllocationResponse(
        group_name=allocation.group_name,
        course_codes=option.course_codes,
    )


def _requirement_allocation_responses(
    curriculum: Curriculum,
    completed: set[str],
) -> list[RequirementAllocationResponse] | None:
    allocations = curriculum.find_allocation(completed)
    if allocations is None:
        return None
    return [
        _requirement_allocation_response(allocation)
        for allocation in allocations
    ]


def _curriculum_progress_response(
    progress: CurriculumProgress,
) -> CurriculumProgressResponse:
    curriculum = progress.curriculum
    completed = progress.completed
    allocations = _requirement_allocation_responses(curriculum, completed)
    return CurriculumProgressResponse(
        name=curriculum.name,
        is_complete=allocations is not None,
        completed_course_codes=sorted(completed),
        required_groups=[
            _required_group_progress_response(group, completed)
            for group in curriculum.required_groups
        ],
        choice_groups=[
            _choice_group_progress_response(group, completed)
            for group in curriculum.choice_groups
        ],
        option_groups=[
            _option_group_progress_response(group, completed)
            for group in curriculum.option_groups
        ],
        allocations=allocations,
    )


@app.get("/courses", response_model=list[CourseResponse])
def get_courses(
    connection: sqlite3.Connection = Depends(get_database),
) -> list[Course]:
    return load_courses(connection)


@app.get("/completed", response_model=list[str])
def get_completed_courses(
    connection: sqlite3.Connection = Depends(get_database),
) -> list[str]:
    return sorted(load_completed_courses(connection))


@app.post("/completed", status_code=204)
def complete_course(
    request: CourseCompletionRequest,
    connection: sqlite3.Connection = Depends(get_database),
) -> None:
    try:
        mark_course_completed_from_database(connection, request.course_code)
    except CourseNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/plan", response_model=list[CourseResponse])
def get_next_semester_plan(
    max_credits: int = Query(default=15, gt=0),
    connection: sqlite3.Connection = Depends(get_database),
) -> list[Course]:
    return plan_next_semester_from_database(connection, max_credits)


@app.get("/plan/all", response_model=list[list[CourseResponse]])
def get_full_plan(
    max_credits: int = Query(default=15, gt=0),
    connection: sqlite3.Connection = Depends(get_database),
) -> list[list[Course]]:
    return plan_multiple_semesters_from_database(connection, max_credits)


@app.get("/validation", response_model=ValidationResponse)
def get_validation(
    connection: sqlite3.Connection = Depends(get_database),
) -> ValidationResponse:
    result = validate_course_graph(load_courses(connection))
    missing_prerequisites = [
        MissingPrerequisiteResponse(
            course_code=course_code,
            prerequisite_code=prerequisite_code,
        )
        for course_code, prerequisite_code in result.missing_prerequisites
    ]
    return ValidationResponse(
        is_valid=result.is_valid,
        missing_prerequisites=missing_prerequisites,
        cycle_path=result.cycle_path,
    )


@app.get("/health")
def get_health() -> dict[str, str]:
    return {"status": "ok"}
