# Purdue CS Degree Planner

A Python and SQLite project for planning Purdue CS courses from prerequisites,
completed courses, and semester credit limits.

## Current CLI Workflow

```powershell
degree-planner --database data/planner.db import tests/fixtures/courses.csv
degree-planner --database data/planner.db validate
degree-planner --database data/planner.db plan-all --max-credits 7
degree-planner --database data/planner.db complete "CS 18000"
degree-planner --database data/planner.db plan --max-credits 15
degree-planner --database data/planner.db progress data/purdue_software_engineering.json
degree-planner --database data/planner.db courses
degree-planner --database data/planner.db completed
```

## Multi-Semester Planning

`plan` selects one semester. `plan-all` schedules all unfinished courses in the
loaded catalog across multiple semesters. Both commands default to a maximum of
15 credits per semester; use `--max-credits` to choose a different limit.

With the sample CSV imported into a fresh database and no courses marked
completed, `plan-all --max-credits 7` displays:

```text
Semester 1 (4 credits)
  CS 18000: Problem Solving (4 credits)
Semester 2 (3 credits)
  CS 18200: Foundations (3 credits)
```

Prerequisites must be completed before a semester begins. Generating a plan does
not change saved completion records. After marking CS 18000 completed, the same
command returns one semester containing only CS 18200.

An empty plan displays `No remaining courses to plan`. Invalid prerequisite
graphs, nonpositive credit limits, and courses that cannot fit within the credit
limit produce an error message.

The planner assumes full-semester courses and uses greedy selection in
topological order. It does not guarantee the fewest semesters or account for
term-specific course offerings. The sample CSV is test data, not a complete
Purdue catalog, and `plan-all` does not evaluate degree requirements.

## Curriculum Progress

`progress` compares courses saved by the `complete` command with a combined
curriculum JSON file. It reports the overall curriculum status followed by the
status of every required-course, course-choice, and course-option group. When
the curriculum is complete, it also shows which course or paired option was
allocated to each requirement without counting a course twice.

```powershell
degree-planner --database data/planner.db progress data/purdue_software_engineering.json
```

The included Purdue Software Engineering data currently models:

- The six-course Purdue CS core.
- The separate CS 19300 tools requirement.
- The fixed Software Engineering track courses: CS 30700, CS 38100, CS 40700,
  and CS 40800.
- The requirement to complete one of CS 35200 or CS 35400.
- The Software Engineering elective list, including CS 31100 and CS 41100 as
  one paired option.
- Purdue's rule that one course cannot count for both required and elective
  credit.

The data is based on Purdue's [CS degree requirements](https://www.cs.purdue.edu/undergraduate/curriculum/bachelor.html)
and [Software Engineering track requirements](https://www.cs.purdue.edu/undergraduate/curriculum/track-softengr-fall2023.html).
The file is a verified departmental snapshot, not a complete degree audit.
Non-CS degree requirements, minimum grades, approved senior-project
substitutions, course offerings, and a full 2026 catalog audit are not yet
modeled.

## Run Tests

```powershell
python -m pytest
```
