class DuplicateCourseError(ValueError):
    pass


class CourseNotFoundError(ValueError):
    pass


class RequirementsLoadError(Exception):
    pass
