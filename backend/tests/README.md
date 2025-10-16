# Backend Test Infrastructure

## Overview

This directory contains comprehensive test coverage for the Reserve Flow AI 2026 backend, focusing on database layer operations, API endpoints, authentication, and business logic.

## Test Statistics

- **Total Tests**: 563
- **Backend Coverage**: 90%
- **Test Files**: 140+
- **Focused "Residual" Tests**: 42 files

## Test Organization

### Core Test Categories

1. **Database Layer Tests** (`test_database_*.py`)
   - CRUD operations for all entities
   - Ownership validation
   - Pagination and filtering
   - Error handling and edge cases
   - Audit logging

2. **API Tests** (`test_api*.py`, `test_integration_*.py`)
   - Endpoint functionality
   - Request/response validation
   - Error mapping (DB errors to HTTP status codes)
   - Authentication and authorization

3. **Service Layer Tests** (`test_*_service*.py`)
   - Authentication service
   - Token service
   - User service
   - Business logic validation

4. **Repository Tests** (`test_*_repository*.py`)
   - Data access patterns
   - Query building
   - Error handling

## Test Patterns

All tests follow a **triage-driven pattern** with five key test cases:

### 1. Mock-Mode Tests
Tests behavior when `db.client` is `None` (no database connection).

```python
def test_get_project_evidence_client_none():
    database.db.client = None
    res = database.db.get_project_evidence(uuid4_str(), uuid4_str())
    assert isinstance(res, list) and res == []
```

### 2. Ownership-Negative Tests
Tests unauthorized access scenarios.

```python
def test_get_project_evidence_ownership_negative():
    database.db.client = FakeClient({"projects": []})
    res = database.db.get_project_evidence(uuid4_str(), uuid4_str())
    assert res == []
```

### 3. Success Tests
Tests happy path with filters, pagination, and audit logging.

```python
def test_get_project_evidence_success_filters_and_pagination():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    evs = [
        {"id": uuid4_str(), "project_id": proj_id, "evidence_type": "photo"},
        {"id": uuid4_str(), "project_id": proj_id, "evidence_type": "doc"},
    ]
    client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "evidence": evs
    })
    database.db.client = client
    
    res_all = database.db.get_project_evidence(proj_id, profile_id)
    assert all(isinstance(x, Evidence) for x in res_all)
    
    res_filtered = database.db.get_project_evidence(
        proj_id, profile_id, evidence_type="photo"
    )
    assert all(x.evidence_type == "photo" for x in res_filtered)
    
    res_paginated = database.db.get_project_evidence(
        proj_id, profile_id, skip=0, limit=1
    )
    assert len(res_paginated) <= 1
```

### 4. Data-Error Tests
Tests handling of data validation errors (AttributeError, ValueError, etc.).

```python
def test_get_project_evidence_data_error():
    class BrokenQuery:
        def execute(self):
            raise AttributeError("bad data")
    
    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "evidence":
                return BrokenQuery()
            return FakeClient({}).table(name)
    
    database.db.client = BrokenClient({})
    res = database.db.get_project_evidence(uuid4_str(), uuid4_str())
    assert res == []
```

### 5. Unexpected-Exception Tests
Tests that unexpected exceptions are wrapped in `DatabaseError`.

```python
def test_get_project_evidence_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def execute(self):
            raise Exception("boom")
    
    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.get_project_evidence(project_id, profile_id)
```

## Test Harness (conftest.py)

The test harness provides:

### FakeClient
Mock Supabase client for testing without a real database.

```python
client = FakeClient({
    "projects": [{"id": "p1", "profile_id": "u1"}],
    "evidence": [{"id": "e1", "project_id": "p1"}]
})
database.db.client = client
```

### FakeQuery
Mock query builder that mimics Supabase query patterns.

**Key Feature: Inclusive Range Slicing**

The `.range()` method implements Supabase's inclusive end behavior:

```python
# range(0, 4) returns items at indices 0, 1, 2, 3, 4 (5 items total)
query = FakeQuery(data=items)
result = query.range(0, 4).execute()
# Python slice: data[0:(4+1)] = data[0:5]
```

Implementation details:
- `range(start, end)`: Returns items from `start` to `end` **inclusive**
- `range(start, None)`: Returns items from `start` to the end
- Handles both positional and keyword arguments
- Coerces arguments to integers when possible

### Helper Functions

- `uuid4_str()`: Generate UUID strings for test data
- `FakeResponse`: Mock response objects

## Running Tests

### Run All Tests
```bash
cd /home/runner/work/reserve_flow_ai_2026/reserve_flow_ai_2026
python -m pytest backend/tests
```

### Run Specific Test File
```bash
python -m pytest backend/tests/test_database_get_project_evidence_residual.py
```

### Run Tests with Coverage
```bash
python -m pytest backend/tests \
  --cov=backend \
  --cov-report=xml:backend/coverage.xml \
  --cov-report=html:backend/htmlcov \
  --cov-report=term-missing
```

### Run Tests in Quiet Mode
```bash
python -m pytest backend/tests -q
```

### Run Tests with Verbose Output
```bash
python -m pytest backend/tests -v
```

## Coverage Reports

- **XML Report**: `backend/coverage.xml`
- **HTML Report**: `backend/htmlcov/index.html`
- **Terminal Output**: Displayed after test run with `--cov-report=term-missing`

### Viewing HTML Coverage Report

```bash
# Open in browser (Linux)
xdg-open backend/htmlcov/index.html

# Open in browser (macOS)
open backend/htmlcov/index.html

# Open in browser (Windows)
start backend/htmlcov/index.html
```

## Test File Naming Conventions

- `test_*.py`: All test files start with `test_`
- `*_residual.py`: Focused tests with comprehensive triage-driven patterns
- `*_unit.py`: Unit tests with mocked dependencies
- `*_integration.py`: Integration tests with multiple components

## Example Test Files

### Comprehensive "Residual" Tests
- `test_database_get_project_evidence_residual.py`
- `test_database_get_meeting_residual.py`
- `test_database_create_media_file_residual.py`
- `test_database_update_component_residual.py`
- `test_database_delete_inspection_residual.py`

### Database CRUD Tests
- `test_database_projects.py`
- `test_database_components.py`
- `test_database_evidence.py`
- `test_database_inspections.py`
- `test_database_meetings.py`

### API Endpoint Tests
- `test_api.py`
- `test_api_db_error_mapping.py`
- `test_integration_endpoints.py`
- `test_endpoint_ownership.py`

### Authentication Tests
- `test_auth.py`
- `test_auth_service.py`
- `test_auth_repository.py`
- `test_token_service_full.py`

## Continuous Integration

Tests are automatically run in CI/CD pipeline with:
- Test execution
- Coverage reporting
- Coverage threshold enforcement (80% minimum)

## Best Practices

1. **Follow the triage-driven pattern** for all new DB tests
2. **Use descriptive test names** that explain what is being tested
3. **Test both success and failure paths**
4. **Mock external dependencies** using FakeClient and FakeQuery
5. **Verify error handling** with explicit exception checks
6. **Test ownership validation** for all data access operations
7. **Test pagination** where applicable
8. **Verify audit logging** for create/update/delete operations

## Contributing

When adding new tests:
1. Follow existing patterns in similar test files
2. Add all five triage-driven test cases
3. Update this README if introducing new patterns
4. Ensure coverage doesn't drop below 80%
5. Run tests locally before committing

## Troubleshooting

### Tests Failing Locally

1. Check that dependencies are installed:
   ```bash
   pip install -r backend/requirements.txt
   pip install pytest pytest-cov
   ```

2. Verify Python version (3.9+):
   ```bash
   python --version
   ```

3. Clear pytest cache:
   ```bash
   rm -rf backend/.pytest_cache backend/__pycache__
   ```

### Coverage Not Matching CI

1. Run tests from repository root:
   ```bash
   cd /home/runner/work/reserve_flow_ai_2026/reserve_flow_ai_2026
   python -m pytest backend/tests --cov=backend
   ```

2. Check that all test files are being collected:
   ```bash
   python -m pytest backend/tests --collect-only
   ```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)

---

**Last Updated**: October 2025  
**Backend Coverage**: 90%  
**Total Tests**: 563
