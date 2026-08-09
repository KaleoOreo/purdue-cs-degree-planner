def parse_prerequisites(value: str) -> list[str]:
    if not value:
        return []

    return [
        prerequisite.strip()
        for prerequisite in value.split(";")
    ]
