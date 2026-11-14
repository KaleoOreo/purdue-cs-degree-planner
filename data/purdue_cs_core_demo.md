# Purdue CS core planning demo

`purdue_cs_core_demo.csv` is a limited, source-backed example for the
West Lafayette/Indianapolis CS core and the separate CS 19300 tools requirement.
It is not a complete course catalog or degree audit. Checked 2026-11-14.

- [CS degree requirements](https://www.cs.purdue.edu/undergraduate/curriculum/bachelor.html): course names, CS credits, and CS 19300.
- [CS prerequisite flowchart](https://cs.purdue.edu/undergraduate/docs/cs-prereq-flowchart-2024.pdf): selected strict core prerequisite edges.
- [Purdue Mathematics MA 16100](https://www.math.purdue.edu/academic/courses/coursepage?course=16100&subject=MA): title and five credits.

The CSV records only prerequisites that must be completed before a course.
It does not enforce MA 16100 alongside CS 18000, minimum grades, math placement,
alternative math credit, campus restrictions, or term offerings. MA 16100 is
shown without its placement conditions. Do not use the resulting plan as
enrollment advice.

For a fresh local demo database, run:

```powershell
degree-planner --database data/planner.db import data/purdue_cs_core_demo.csv
degree-planner --database data/planner.db validate
degree-planner --database data/planner.db plan-all --max-credits 15
```
