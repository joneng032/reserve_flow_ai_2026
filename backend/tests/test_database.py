"""
Tests for database operations
"""
import os
import sys
from unittest.mock import Mock, patch

import pytest

# Ensure backend package root is on sys.path for imports when running tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import Database, db


@pytest.mark.unit
class TestDatabaseInitialization:
    """Test database initialization"""

    @patch("database.create_client")
    def test_database_initialization_success(self, mock_create_client):
        """Test successful database initialization"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        with patch.dict(
            "os.environ", {"SUPABASE_URL": "test_url", "SUPABASE_ANON_KEY": "test_key"}
        ):
            test_db = Database()
            assert test_db.client == mock_client
            mock_create_client.assert_called_once_with("test_url", "test_key")

    def test_database_initialization_missing_env_vars(self):
        """Test database initialization with missing environment variables"""
        with patch.dict("os.environ", {}, clear=True):
            # Database should be instantiable in mock mode and should set client to None
            db_instance = Database()
            assert db_instance.client is None

    def test_database_initialization_strict_mode_raises(self):
        """When DB_STRICT_INIT is set, Database() should raise if env vars missing"""
        with patch.dict("os.environ", {"DB_STRICT_INIT": "1"}, clear=True):
            with pytest.raises(
                ValueError, match="SUPABASE_URL and SUPABASE_ANON_KEY must be set"
            ):
                Database()


@pytest.mark.unit
class TestProjectOperations:
    """Test project database operations"""

    def test_get_projects_mock_mode(self):
        """Test getting projects in mock mode"""
        # Database is in mock mode when client is None
        if db.client is None:
            projects = db.get_projects("test_user")
            assert isinstance(projects, list)
            # Should return mock data

    def test_create_project_mock_mode(self):
        """Test creating project in mock mode"""
        if db.client is None:
            from uuid import uuid4

            project_data = {
                "name": "Test Project",
                "client_name": "Test Client",
                "address": "123 Test St",
                "current_reserve_balance": 10000.0,
                "profile_id": str(uuid4()),
            }

            # Mock the ProjectCreate import
            from models import ProjectCreate

            create_data = ProjectCreate(**project_data)

            result = db.create_project(create_data)
            assert result is not None
            assert result.name == "Test Project"


@pytest.mark.unit
class TestComponentOperations:
    """Test component database operations"""

    def test_get_project_components_mock_mode(self):
        """Test getting components in mock mode"""
        if db.client is None:
            components = db.get_project_components("test_project", "test_user")
            assert isinstance(components, list)

    def test_create_component_mock_mode(self):
        """Test creating component in mock mode"""
        if db.client is None:
            from decimal import Decimal
            from uuid import uuid4

            from models import ComponentCreate

            component_data = ComponentCreate(
                project_id=uuid4(),
                name="Test Component",
                category="Test Category",
                base_cost=Decimal("5000.0"),
            )

            result = db.create_component(component_data, "test_user")
            assert result is not None
            assert result.name == "Test Component"


@pytest.mark.unit
class TestAnalyticsOperations:
    """Test analytics operations"""

    def test_get_cost_analysis_mock_mode(self):
        """Test cost analysis in mock mode"""
        if db.client is None:
            analysis = db.get_cost_analysis("test_project", "test_user")
            assert analysis is not None
            assert hasattr(analysis, "total_components")
            assert hasattr(analysis, "total_value")
            assert hasattr(analysis, "average_cost")

    def test_get_reserve_analysis_mock_mode(self):
        """Test reserve analysis in mock mode"""
        if db.client is None:
            analysis = db.get_reserve_analysis("test_project", "test_user")
            assert analysis is not None
            assert hasattr(analysis, "percent_funded")
            assert hasattr(analysis, "total_reserve_balance")
            assert hasattr(analysis, "total_liability")


@pytest.mark.unit
class TestCategoryOperations:
    """Test category operations"""

    def test_get_project_categories_mock_mode(self):
        """Test getting categories in mock mode"""
        if db.client is None:
            categories = db.get_project_categories("test_project", "test_user")
            assert isinstance(categories, list)

    def test_create_category_mock_mode(self):
        """Test creating category in mock mode"""
        if db.client is None:
            from uuid import uuid4

            from models import CategoryCreate

            category_data = CategoryCreate(project_id=uuid4(), name="Test Category")

            result = db.create_category(category_data, "test_user")
            assert result is not None
            assert result.name == "Test Category"


@pytest.mark.unit
class TestUtilityOperations:
    """Test utility operations"""

    def test_get_metro_multipliers_mock_mode(self):
        """Test getting metro multipliers in mock mode"""
        if db.client is None:
            multipliers = db.get_metro_multipliers()
            assert isinstance(multipliers, list)

    def test_get_component_catalog_mock_mode(self):
        """Test getting component catalog in mock mode"""
        if db.client is None:
            catalog = db.get_component_catalog()
            assert isinstance(catalog, list)
