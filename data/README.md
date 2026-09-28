# Curriculum Data Scope

Phase 6 targets Purdue West Lafayette's Computer Science B.S., using the 2026
catalog and Software Engineering as the first supported track. Implement the
shared CS core first, then track requirements. This is a development target;
complete support and catalog verification are not yet implemented.

## Sources and Verification

Sources inspected on 2026-09-28:

- [College of Science curriculum resources](https://www.purdue.edu/science/Current_Students/majors/index.html): links to the 2026 catalog and degree progression guide. The catalog link returned HTTP 403 during inspection, so its detailed requirements remain unverified.
- [CS degree requirements](https://www.cs.purdue.edu/undergraduate/curriculum/bachelor.html): departmental core and track overview.
- [Software Engineering track](https://www.cs.purdue.edu/undergraduate/curriculum/track-softengr-fall2023.html): departmental page labeled Fall 2023 and Forward; reconcile against the targeted catalog before treating it as the complete 2026 rules.

Record sources and applicable catalog years alongside curriculum data. Resolve
source disagreements explicitly rather than combining rules from different years.
Do not infer Fall 2028 requirements from this development baseline.

## Current Coverage

`tests/fixtures/courses.csv` remains synthetic test data, not a verified catalog.
The current completion records contain course codes only; they do not establish
minimum grades, accepted transfer credit, or satisfaction of full degree rules.
Early course-presence checks must not be presented as complete degree audits.
