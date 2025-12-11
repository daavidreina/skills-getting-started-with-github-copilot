"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to a known state before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball with tryouts and tournaments",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["sarah@mergington.edu", "alex@mergington.edu"]
        },
        "Digital Art": {
            "description": "Create digital artwork and graphic design projects",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["maya@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, scripts, and theatrical performances",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 14,
            "participants": ["rachel@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and scientific exploration",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["jacob@mergington.edu", "zoe@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the get_activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that get_activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9
    
    def test_get_activities_includes_participants(self, client, reset_activities):
        """Test that activities include participant lists"""
        response = client.get("/activities")
        data = response.json()
        assert "participants" in data["Chess Club"]
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupForActivity:
    """Tests for the signup_for_activity endpoint"""
    
    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "Signed up newstudent@mergington.edu for Chess Club" in data["message"]
        
        # Verify participant was added
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client, reset_activities):
        """Test signup fails for nonexistent activity"""
        response = client.post("/activities/Fake%20Activity/signup?email=student@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_duplicate_signup_prevented(self, client, reset_activities):
        """Test that duplicate signups are prevented"""
        # First signup should succeed
        response1 = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_already_registered_student(self, client, reset_activities):
        """Test that already registered students cannot signup twice"""
        response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_with_valid_email_formats(self, client, reset_activities):
        """Test signup with various email formats"""
        emails = [
            "student1@mergington.edu",
            "student.name@mergington.edu",
            "student123@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(f"/activities/Programming%20Class/signup?email={email}")
            assert response.status_code == 200
            assert email in activities["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the unregister_from_activity endpoint"""
    
    def test_successful_unregister(self, client, reset_activities):
        """Test successful unregister from an activity"""
        response = client.post("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered michael@mergington.edu from Chess Club" in data["message"]
        
        # Verify participant was removed
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client, reset_activities):
        """Test unregister fails for nonexistent activity"""
        response = client.post("/activities/Fake%20Activity/unregister?email=student@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_nonexistent_participant(self, client, reset_activities):
        """Test unregister fails for participant not in activity"""
        response = client.post("/activities/Chess%20Club/unregister?email=notregistered@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_allows_new_signup_after(self, client, reset_activities):
        """Test that after unregistering, student can sign up again"""
        # First unregister an existing participant
        response1 = client.post("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        assert response1.status_code == 200
        
        # Now they should be able to sign up again
        response2 = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")
        assert response2.status_code == 200
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]


class TestCapacityValidation:
    """Tests for activity capacity validation"""
    
    def test_capacity_check_on_signup(self, client, reset_activities):
        """Test that signup respects activity capacity"""
        # Fill up an activity (max 1 participant for testing)
        activities["Test Activity"] = {
            "description": "Test activity",
            "schedule": "Test time",
            "max_participants": 1,
            "participants": ["existing@mergington.edu"]
        }
        
        # Try to add another participant when at capacity
        response = client.post("/activities/Test%20Activity/signup?email=new@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "full" in data["detail"]


class TestActivityData:
    """Tests for activity data structure and content"""
    
    def test_activities_have_required_fields(self, client, reset_activities):
        """Test that all activities have required fields"""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_info in activities_data.items():
            assert "description" in activity_info
            assert "schedule" in activity_info
            assert "max_participants" in activity_info
            assert "participants" in activity_info
            assert isinstance(activity_info["participants"], list)
    
    def test_no_duplicate_participants_in_activity(self, client, reset_activities):
        """Test that an activity doesn't have duplicate participants"""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_info in activities_data.items():
            participants = activity_info["participants"]
            assert len(participants) == len(set(participants))
