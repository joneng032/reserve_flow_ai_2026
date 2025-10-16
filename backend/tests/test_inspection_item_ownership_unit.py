from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.main import ensure_belongs_to_project


def test_ensure_belongs_to_project_raises_on_mismatch():
    resource = SimpleNamespace(project_id="other-project")
    with pytest.raises(HTTPException) as exc:
        ensure_belongs_to_project(resource, "my-project", "Inspection item")

    # FastAPI will raise an HTTPException; ensure detail includes 'not found'
    assert hasattr(exc.value, "detail")
    assert "not found" in str(exc.value.detail)
