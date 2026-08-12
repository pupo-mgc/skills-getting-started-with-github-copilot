"""Pytest configuration and fixtures for API tests."""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def test_client():
    """Provide a TestClient for testing the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """Provide a fresh copy of activities data for each test to ensure isolation.
    
    Returns a deep copy of the activities dictionary so tests don't mutate
    the original data, ensuring test isolation and repeatability.
    """
    return copy.deepcopy(activities)


@pytest.fixture
def mock_activities(monkeypatch, fresh_activities):
    """Replace app.activities with fresh test data for each test.
    
    This ensures that modifications to activities during a test don't affect
    other tests. Uses pytest's monkeypatch to inject the fresh data.
    """
    monkeypatch.setattr("src.app.activities", fresh_activities)
    return fresh_activities


@pytest.fixture
def test_emails():
    """Provide test email addresses."""
    return {
        "new_student": "new.student@mergington.edu",
        "existing_student": "michael@mergington.edu",  # Already in Chess Club
        "another_student": "another.student@mergington.edu",
    }


@pytest.fixture
def test_activities_names():
    """Provide test activity names."""
    return {
        "valid": "Chess Club",
        "invalid": "Nonexistent Club",
    }
