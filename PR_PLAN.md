# Plan to reach >=80% test coverage for backend

Goal
Raise backend test coverage to at least 80% before opening a PR merge.

Strategy

Phases & priority

Engineering details

Estimate & cadence

Acceptance criteria

Risks & mitigations

Next immediate steps
# Plan to reach >=80% test coverage for backend

## Goal

Raise backend test coverage to at least 80% before opening a PR merge.

## Strategy

- Continue adding focused test batches that target groups of related functions in `backend/database.py`.
- Prefer high-impact functions first (large bodies, many branches, audit/log creation).
- For each function group: write happy-path tests, then 1–2 negative/error-path tests (ownership, missing project, validation errors).

## Phases & priority

1. Audit & logging (high) — cover create_audit_log, get_project_audit_logs, and branches where entity_type filters are used. (2–3 tests)

2. Components / Tags / Component Tags (high) — exercise create/update/delete and tag joins. Add negative ownership checks. (6–8 tests)

3. Media & Evidence (high) — add detailed media CRUD, get_project_media_files filters, evidence flows. (6–8 tests)

4. Inspections & Items (medium) — create_inspection, create_inspection_item, update/delete branches. (4–6 tests)

5. Meetings, Interviews, Communications (medium) — ensure required fields and audit creation. (4–6 tests)

6. Analytics (high) — cost and reserve analysis, edge cases (zero components, division by zero). (4–6 tests)

7. Templates, Field Definitions, Tags (low-medium) — CRUD via FakeClient insertion and expected negative tests where db helpers exist. (4–6 tests)

8. Remaining utilities & helpers (low) — any small functions not covered by above. (misc tests)
### PR Plan to reach 80% backend coverage

#### Overview

The `backend/database.py` file is the main target. It's large and contains many helper functions that touch DB CRUD, auditing, analytics, and business logic. We'll add focused, small test files that exercise a handful of related functions at a time.

#### Guiding rules

1) Keep tests small and focused (6-15 functions per batch)
2) Prefer deterministic FakeClient seeding to avoid flaky network calls
3) For each new test file: include at least one happy-path and one negative/edge-path test
4) Run focused pytest for changed tests until green before moving to the next batch
5) Update this plan and `PR_SUMMARY.md` as progress is made

#### Batch prioritization (next immediate batches)

Batch A: Audit & logging helpers + cost/reserve helpers
Batch B: Components and their tag/template flows
Batch C: Media, evidence, and inspection helpers
Batch D: Meetings/interviews/communications
Batch E: Analytics (cost/reserve/reporting edge cases)
Batch F: Templates and field definitions
Batch G: Remaining utility and backup helpers

#### Acceptance criteria

- All tests pass locally under pytest
- Coverage report (backend) >= 80% before PR is created
- Tests should not depend on external network access

#### How to run locally

1. From the repo root: `pytest -q --maxfail=1 --disable-warnings`
2. To get coverage: `pytest --cov=backend --cov-report=xml:coverage.xml --cov-report=html`

#### Notes

- The FakeClient is intentionally minimal. If you find gaps while writing tests, extend it only for the behavior you need.
- Be cautious when adding tests that rely on deep join semantics — the FakeClient only supports simple dotted-key join emulation.

#### Detailed remaining tasks

1. Audit & logging: write tests for create_audit_log, get_project_audit_logs, and audit read filters
2. Components: exercise create_component, update_component, delete_component, get_component_catalog, and tag/template associations
3. Media/Evidence: create_media_file, get_media_file, update_media_file, delete_media_file, and evidence link flows
4. Inspections/Checklist: inspection CRUD, inspection item CRUD, and related analytics
5. Meetings/Interviews/Communications: create/get/update/delete and negative ownership/permission tests
6. Analytics: cost and reserve reporting, negative paths when values are missing
7. Templates/Field Definitions: CRUD and validation
8. Backup/Restore helpers: if present, add tests to verify export/import logic

#### When to open the PR

Open the PR from `copilot-ruleset-branch` once backend coverage >= 80% and all tests pass.

#### Safety note

Be careful not to change production code in this PR — the goal is to add tests and harness only. Any required code changes should be discussed and landed separately.
