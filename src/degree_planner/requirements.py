def find_missing_required_courses(
    required: set[str],
    completed: set[str],
) -> set[str]:
    return required - completed
