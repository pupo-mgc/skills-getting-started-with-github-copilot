"""Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

import pytest


class TestUnregisterFromActivity:
    """Tests for unregistering students from activities."""

    def test_unregister_success_with_valid_activity_and_email(self, test_client, mock_activities):
        """Test successful unregister with valid activity and registered email."""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = test_client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]

    def test_unregister_removes_participant_from_activity(self, test_client, mock_activities):
        """Test that unregister actually removes the participant from the activity."""
        email = "michael@mergington.edu"
        
        # Verify participant is in activity before unregister
        activities_before = test_client.get("/activities").json()
        assert email in activities_before["Chess Club"]["participants"]
        
        # Unregister
        response = test_client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_after = test_client.get("/activities").json()
        assert email not in activities_after["Chess Club"]["participants"]

    def test_unregister_from_nonexistent_activity_returns_404(self, test_client, mock_activities):
        """Test that unregister from non-existent activity returns 404."""
        response = test_client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_unregister_not_registered_student_returns_400(self, test_client, mock_activities):
        """Test that unregistering a student who isn't signed up returns 400."""
        response = test_client.delete(
            "/activities/Tennis Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not" in data["detail"].lower()

    def test_unregister_preserves_other_participants(self, test_client, mock_activities):
        """Test that unregistering one participant doesn't affect others."""
        # Chess Club has michael and daniel
        michael_email = "michael@mergington.edu"
        daniel_email = "daniel@mergington.edu"
        
        # Unregister michael
        response = test_client.delete(
            "/activities/Chess Club/unregister",
            params={"email": michael_email}
        )
        assert response.status_code == 200
        
        # Verify daniel is still there
        activities = test_client.get("/activities").json()
        assert michael_email not in activities["Chess Club"]["participants"]
        assert daniel_email in activities["Chess Club"]["participants"]

    def test_unregister_then_signup_again(self, test_client, mock_activities):
        """Test that a student can unregister and then sign up again."""
        email = "michael@mergington.edu"
        
        # Unregister
        response1 = test_client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Verify unregistered
        activities = test_client.get("/activities").json()
        assert email not in activities["Chess Club"]["participants"]
        
        # Sign up again
        response2 = test_client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify signed up again
        activities = test_client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]

    def test_unregister_invalid_activity_name_returns_404(self, test_client, mock_activities):
        """Test various invalid activity names return 404."""
        invalid_names = ["", "NonexistentClub", "chess club", "CHESS CLUB"]
        
        for invalid_name in invalid_names:
            response = test_client.delete(
                f"/activities/{invalid_name}/unregister",
                params={"email": "student@mergington.edu"}
            )
            assert response.status_code == 404, f"Expected 404 for '{invalid_name}'"

    def test_unregister_all_participants_one_by_one(self, test_client, mock_activities):
        """Test unregistering all participants from an activity one by one."""
        activity = "Chess Club"
        
        # Get initial participants
        activities = test_client.get("/activities").json()
        participants = list(activities[activity]["participants"])
        
        # Unregister each participant
        for email in participants:
            response = test_client.delete(
                f"/activities/{activity}/unregister",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all are unregistered
        activities = test_client.get("/activities").json()
        assert len(activities[activity]["participants"]) == 0

    def test_unregister_empty_email_returns_400(self, test_client, mock_activities):
        """Test that empty email for unregister is handled appropriately."""
        response = test_client.delete(
            "/activities/Chess Club/unregister",
            params={"email": ""}
        )
        
        # Empty string was never registered, so should return 400
        assert response.status_code == 400
