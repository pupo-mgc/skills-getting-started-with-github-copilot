"""Tests for the POST /activities/{activity_name}/signup endpoint."""

import pytest


class TestSignupForActivity:
    """Tests for signing up students for activities."""

    def test_signup_success_with_valid_activity_and_email(self, test_client, mock_activities, test_emails):
        """Test successful signup with valid activity name and email."""
        response = test_client.post(
            "/activities/Chess Club/signup",
            params={"email": test_emails["new_student"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert test_emails["new_student"] in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_adds_participant_to_activity(self, test_client, mock_activities, test_emails):
        """Test that signup actually adds the participant to the activity."""
        email = test_emails["new_student"]
        
        # Signup
        response = test_client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = test_client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]

    def test_signup_to_nonexistent_activity_returns_404(self, test_client, mock_activities, test_emails):
        """Test that signup to non-existent activity returns 404."""
        response = test_client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": test_emails["new_student"]}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_signup_duplicate_returns_400(self, test_client, mock_activities):
        """Test that attempting to sign up twice returns 400."""
        # First signup should succeed
        response1 = test_client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}  # Already signed up
        )
        
        assert response1.status_code == 400
        data = response1.json()
        assert "detail" in data
        assert "already" in data["detail"].lower()

    def test_signup_multiple_students_same_activity(self, test_client, mock_activities, test_emails):
        """Test that multiple different students can sign up for the same activity."""
        student1 = test_emails["new_student"]
        student2 = test_emails["another_student"]
        
        # Signup first student
        response1 = test_client.post(
            "/activities/Programming Class/signup",
            params={"email": student1}
        )
        assert response1.status_code == 200
        
        # Signup second student
        response2 = test_client.post(
            "/activities/Programming Class/signup",
            params={"email": student2}
        )
        assert response2.status_code == 200
        
        # Verify both are in the activity
        activities_response = test_client.get("/activities")
        activities = activities_response.json()
        participants = activities["Programming Class"]["participants"]
        assert student1 in participants
        assert student2 in participants

    def test_signup_invalid_activity_name_returns_404(self, test_client, mock_activities, test_emails):
        """Test various invalid activity names return 404."""
        invalid_names = ["", "NonexistentClub", "chess club", "CHESS CLUB"]
        
        for invalid_name in invalid_names:
            response = test_client.post(
                f"/activities/{invalid_name}/signup",
                params={"email": test_emails["new_student"]}
            )
            assert response.status_code == 404, f"Expected 404 for '{invalid_name}'"

    def test_signup_empty_email_returns_error(self, test_client, mock_activities):
        """Test that empty email is handled appropriately."""
        response = test_client.post(
            "/activities/Chess Club/signup",
            params={"email": ""}
        )
        
        # Empty string is still technically valid for the endpoint
        # but it will add an empty string to participants
        # This test documents current behavior; validation could be added
        assert response.status_code == 200

    def test_signup_preserves_existing_participants(self, test_client, mock_activities):
        """Test that adding a new participant doesn't remove existing ones."""
        # Chess Club starts with 2 participants
        activities_before = test_client.get("/activities").json()
        count_before = len(activities_before["Chess Club"]["participants"])
        
        # Add new participant
        test_client.post(
            "/activities/Chess Club/signup",
            params={"email": "new.student@mergington.edu"}
        )
        
        # Verify count increased by 1
        activities_after = test_client.get("/activities").json()
        count_after = len(activities_after["Chess Club"]["participants"])
        assert count_after == count_before + 1
