"""Tests for the GET /activities endpoint."""

import pytest


class TestGetActivities:
    """Tests for retrieving all activities."""

    def test_get_activities_returns_all_activities(self, test_client, mock_activities):
        """Test that GET /activities returns all activities in the system."""
        response = test_client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(mock_activities)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_response_structure(self, test_client, mock_activities):
        """Test that each activity has the expected fields."""
        response = test_client.get("/activities")
        data = response.json()
        
        # Check a specific activity structure
        chess_club = data.get("Chess Club")
        assert chess_club is not None
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_preserves_participants(self, test_client, mock_activities):
        """Test that participant lists are correctly returned."""
        response = test_client.get("/activities")
        data = response.json()
        
        # Chess Club should have 2 initial participants
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_get_activities_multiple_calls_consistent(self, test_client, mock_activities):
        """Test that multiple calls return consistent data without mutations."""
        response1 = test_client.get("/activities")
        data1 = response1.json()
        
        response2 = test_client.get("/activities")
        data2 = response2.json()
        
        assert data1 == data2

    def test_get_activities_empty_activities_handled(self, test_client, monkeypatch):
        """Test behavior when activities dict is empty."""
        monkeypatch.setattr("src.app.activities", {})
        
        response = test_client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
