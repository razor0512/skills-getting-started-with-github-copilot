import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


def test_get_activities_returns_activity_catalog(client):
    # Arrange
    # No setup required for a read-only listing.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12
    assert "michael@mergington.edu" in payload["Chess Club"]["participants"]


def test_signup_for_activity_registers_student(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_already_registered_student_returns_400(client):
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_student(client):
    # Arrange
    activity_name = "Chess Club"
    email = "tempstudent@mergington.edu"
    activities[activity_name]["participants"].append(email)
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_non_participant_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
