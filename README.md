# Purdue CS Degree Planner

A Python and SQLite project for planning Purdue CS courses from prerequisites,
completed courses, and semester credit limits.

## Current CLI Workflow

```powershell
degree-planner --database data/planner.db import tests/fixtures/courses.csv
degree-planner --database data/planner.db complete "CS 18000"
degree-planner --database data/planner.db plan --max-credits 15
degree-planner --database data/planner.db courses
degree-planner --database data/planner.db completed
```

## Run Tests

```powershell
python -m pytest
```
