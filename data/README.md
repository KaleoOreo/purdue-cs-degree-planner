# Curriculum Data Scope

Phase 6 targets Purdue West Lafayette's Computer Science B.S., using the 2026
catalog and Software Engineering as the first supported track. Implement the
shared CS core first, then track requirements. This is a development target;
complete support and catalog verification are not yet implemented.

## Sources and Verification

Sources inspected on 2026-09-30:

- [College of Science curriculum resources](https://www.purdue.edu/science/Current_Students/majors/index.html): links to the 2026 catalog and degree progression guide. The catalog link returned HTTP 403 during inspection, so its detailed requirements remain unverified.
- [CS degree requirements](https://www.cs.purdue.edu/undergraduate/curriculum/bachelor.html): departmental core and track overview.
- [Software Engineering track](https://www.cs.purdue.edu/undergraduate/curriculum/track-softengr-fall2023.html): departmental page labeled Fall 2023 and Forward; reconcile against the targeted catalog before treating it as the complete 2026 rules.

Record sources and applicable catalog years alongside curriculum data. Resolve
source disagreements explicitly rather than combining rules from different years.
Do not infer Fall 2028 requirements from this development baseline.

The 2026 catalog link still returned HTTP 403 on recheck. The linked 2026 CS
Degree Progression Guide redirected to Microsoft sign-in and could not be read.
Departmental pages are verified sources for the rules below, but do not establish
complete verification of the targeted catalog.

## Purdue Rules Guiding Phase 6

The linked departmental sources establish these implementation requirements:

- The six-course core contains CS 18000, CS 18200, CS 24000, CS 25000,
  CS 25100, and CS 25200. CS 19300 is separately required for beginning majors;
  the six-course group must not be presented as the entire major.
- The Software Engineering track lists CS 30700, CS 38100, CS 40800, and
  CS 40700, plus a choice of CS 35200 or CS 35400, and one elective option.
- CS 31100 together with CS 41100 satisfies one elective option; neither course
  alone satisfies that paired option.
- A course cannot count for both required and elective credit. Independent
  choice-group counts alone cannot enforce this restriction.
- Approved senior-project substitutions require track-chair approval; completion
  codes alone cannot establish that approval.

These are requirements for future implementation, not claims of current support.
Verify course credits and prerequisite conditions separately from requirement
membership. Never infer prerequisite edges or term availability from list order
or suggested semester positions. Synthetic test cases remain useful for checking
algorithms, but must not be distributed as verified Purdue curriculum data.

## Current Coverage

`purdue_cs_core.json` records the six courses in the department's "Core
Requirements (21)" table, with its source URL and verification date. It describes
required course membership only, not prerequisites, grades, or a full degree.
The source also specifies a minimum grade of C for major courses; the current
course-code completion model does not verify that condition. Other requirements
outside this six-course table are not included. This is a departmental snapshot,
not a fully verified 2026 catalog dataset.

`tests/fixtures/courses.csv` remains synthetic test data, not a verified catalog.
The current completion records contain course codes only; they do not establish
minimum grades, accepted transfer credit, or satisfaction of full degree rules.
Early course-presence checks must not be presented as complete degree audits.
