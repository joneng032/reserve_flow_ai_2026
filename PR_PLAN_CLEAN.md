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

## Engineering details

- Use `backend/tests/conftest.py` FakeClient to shape table_data for each test so tests run offline.
- When a DB helper isn't present (e.g., create_tag), use direct `database.db.client.table(...).insert(...)` to exercise table behaviors.
- For Pydantic UUID fields, always supply valid uuid4 strings (use `uuid4_str()` helper in tests).
- For audit assertions: monkeypatch `database.Database.create_audit_log` where necessary to capture audit payloads without relying on DB writes.

## Estimate & cadence

- Implement groups in parallel-ish batches of 4–8 tests, run focused pytest, fix failures, and proceed. Each batch should take ~10–30 minutes to implement and stabilize depending on failures.

## Acceptance criteria

- All tests pass locally.
- Aggregate coverage reported by pytest-cov >= 80% for the repository (or at least for `backend/` package if CI enforces a subset).

## Risks & mitigations

- FakeClient gaps: extend it incrementally when tests reveal missing behaviors (contains, dotted-key joins, default seeding).
- Pydantic model changes: adapt tests to required fields; prefer using model constructors with required args.

## Next immediate steps

1. Implement Audit & logging tests (small, high-value).

2. Implement Component & Tag tests (more work; high coverage payback).

## How to run locally

1. From the repo root: `pytest -q --maxfail=1 --disable-warnings`

2. To get coverage: `pytest --cov=backend --cov-report=xml:coverage.xml --cov-report=html`

## Detailed remaining tasks

1. Audit & logging: write tests for create_audit_log, get_project_audit_logs, and audit read filters

2. Components: exercise create_component, update_component, delete_component, get_component_catalog, and tag/template associations

3. Media/Evidence: create_media_file, get_media_file, update_media_file, delete_media_file, and evidence link flows

4. Inspections/Checklist: inspection CRUD, inspection item CRUD, and related analytics

5. Meetings/Interviews/Communications: create/get/update/delete and negative ownership/permission tests

6. Analytics: cost and reserve reporting, negative paths when values are missing

7. Templates/Field Definitions: CRUD and validation

8. Backup/Restore helpers: if present, add tests to verify export/import logic

## When to open the PR

Open the PR from `copilot-ruleset-branch` once backend coverage >= 80% and all tests pass.

## Safety note

Be careful not to change production code in this PR — the goal is to add tests and harness only. Any required code changes should be discussed and landed separately.
