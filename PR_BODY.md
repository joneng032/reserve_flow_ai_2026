Copilot ruleset and triage-driven tests

Summary:
- Added a Copilot ruleset and implemented a triage-driven testing workflow to incrementally increase coverage in `backend/database.py`.
- Implemented a Fake DB harness (`backend/tests/conftest.py`) with improved `.range()` slicing to support pagination tests.
- Added focused tests for many database functions (evidence, components, meetings, communications, inspections, media files). See `backend/tests/` for details.

Coverage:
- Repo-wide coverage is currently ~89% (coverage.xml at project root). This meets the repo-wide >=80% gate.

Notes:
- The PR is made from branch `copilot-ruleset-branch` and will update the existing open PR.
- We intentionally committed only tracked and safe changes. There are additional new test files in `backend/tests/` that were generated during triage; please review and let me know if you want them included in this PR.

Next steps:
- Continue the triage loop to cover remaining uncovered lines in `backend/database.py`.
- Optionally add CI badges and a minimal CI workflow to enforce the coverage gate.

Signed-off-by: Automated test agent
