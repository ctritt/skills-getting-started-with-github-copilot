import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module
from src.app import app

client = TestClient(app, follow_redirects=False)
INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(INITIAL_ACTIVITIES)
    yield
    app_module.activities = copy.deepcopy(INITIAL_ACTIVITIES)


def test_root_redirects_to_static_page():
    # Arrange

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_the_activity_catalog():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_adds_a_participant():
    # Arrange

    # Act
    response = client.post("/activities/Chess Club/signup?email=student@example.com")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up student@example.com for Chess Club"
    }
    assert "student@example.com" in app_module.activities["Chess Club"]["participants"]


def test_signup_for_activity_returns_400_for_existing_participant():
    # Arrange

    # Act
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_activity_returns_400_when_activity_is_full():
    # Arrange
    activity = app_module.activities["Chess Club"]
    activity["participants"] = [f"student{i}@example.com" for i in range(activity["max_participants"])]

    # Act
    response = client.post("/activities/Chess Club/signup?email=another@example.com")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_signup_for_activity_returns_400_for_empty_email():
    # Arrange

    # Act
    response = client.post("/activities/Chess Club/signup?email=")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Email is required"


def test_signup_for_activity_returns_404_for_missing_activity():
    # Arrange

    # Act
    response = client.post("/activities/Unknown Activity/signup?email=test@example.com")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_for_activity_returns_404_for_missing_activity():
    # Arrange

    # Act
    response = client.post("/activities/Unknown Activity/unregister?email=test@example.com")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_for_activity_returns_400_for_missing_participant():
    # Arrange

    # Act
    response = client.post("/activities/Chess Club/unregister?email=missing@example.com")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
