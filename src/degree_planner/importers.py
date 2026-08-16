import csv

from degree_planner.models import Course


def parse_prerequisites(value: str) -> list[str]:
    if not value:
        return []

    return [
        prerequisite.strip()
        for prerequisite in value.split(";")
    ]


def course_from_row(row: dict[str, str]) -> Course:
    return Course(
        row["code"],
        row["title"],
        int(row["credits"]),
        row["category"],
        parse_prerequisites(row["prerequisites"]),
    )


def load_courses_from_csv(path: str) -> list[Course]:
    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        return [
            course_from_row(row)
            for row in reader
        ]
