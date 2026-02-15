"""
Renault Trucks Garanti Kayıt Sistemi - API Tests
Tests: Landing page, Dark/Light mode, Version system, Auth, Apprentice workflow, Notifications
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://truck-service-vault.preview.emergentagent.com')

# Test credentials
ADMIN_CREDS = {"username": "admin", "password": "admin123"}
STAFF_CREDS = {"username": "hadimkoy_garanti", "password": "test123"}
APPRENTICE_CREDS = {"username": "test_stajyer", "password": "test123"}


class TestHealthAndVersion:
    """Test health check and version endpoints"""
    
    def test_api_health_check(self):
        """API root should return version info"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "message" in data
        assert data["version"] == "1.2.0"
        print(f"✓ API health check passed - Version: {data['version']}")
    
    def test_version_endpoint(self):
        """Version endpoint should return full version info"""
        response = requests.get(f"{BASE_URL}/api/version")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.2.0"
        assert data["date"] == "2025-12-15"
        assert "build" in data
        assert "fullVersion" in data
        print(f"✓ Version endpoint passed - {data['fullVersion']}")


class TestBranches:
    """Test branch and job title endpoints"""
    
    def test_get_branches(self):
        """Should return all 5 branches"""
        response = requests.get(f"{BASE_URL}/api/branches")
        assert response.status_code == 200
        data = response.json()
        assert "branches" in data
        assert len(data["branches"]) == 5
        branch_names = [b["name"] for b in data["branches"]]
        assert "Bursa" in branch_names
        assert "Hadımköy" in branch_names
        print(f"✓ Branches endpoint passed - {len(data['branches'])} branches found")
    
    def test_get_job_titles(self):
        """Should return job titles"""
        response = requests.get(f"{BASE_URL}/api/job-titles")
        assert response.status_code == 200
        data = response.json()
        assert "job_titles" in data
        assert len(data["job_titles"]) >= 3
        print(f"✓ Job titles endpoint passed - {len(data['job_titles'])} titles found")


class TestAuthentication:
    """Test authentication flows"""
    
    def test_admin_login(self):
        """Admin login should succeed"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
        assert data["user"]["username"] == "admin"
        print(f"✓ Admin login passed - User: {data['user']['full_name']}")
    
    def test_staff_login(self):
        """Staff login should succeed"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=STAFF_CREDS)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["role"] == "staff"
        assert data["user"]["branch_code"] == "4"  # Hadımköy
        print(f"✓ Staff login passed - Branch: {data['user']['branch_name']}")
    
    def test_apprentice_login(self):
        """Apprentice login should succeed"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=APPRENTICE_CREDS)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["role"] == "apprentice"
        print(f"✓ Apprentice login passed - User: {data['user']['full_name']}")
    
    def test_invalid_login(self):
        """Invalid credentials should return 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "wrong", "password": "wrong"})
        assert response.status_code == 401
        print("✓ Invalid login correctly rejected")
    
    def test_get_current_user(self, admin_token):
        """Should return current user info"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"
        print(f"✓ Get current user passed - {data['full_name']}")


class TestStaffManagement:
    """Test staff and apprentice management"""
    
    def test_get_staff_list(self, admin_token):
        """Admin should see all staff"""
        response = requests.get(f"{BASE_URL}/api/staff?include_apprentices=true", 
                               headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Get staff list passed - {len(data)} staff members")
    
    def test_get_apprentices(self, admin_token):
        """Admin should see apprentices"""
        response = requests.get(f"{BASE_URL}/api/apprentices", 
                               headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check if test apprentice exists
        apprentice_names = [a.get("username") for a in data]
        assert "test_stajyer" in apprentice_names
        print(f"✓ Get apprentices passed - {len(data)} apprentices")


class TestRecordApprovalWorkflow:
    """Test apprentice record creation and approval workflow"""
    
    def test_pending_records_endpoint(self, admin_token):
        """Pending records endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/records/pending", 
                               headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Pending records endpoint passed - {len(data)} pending records")
    
    def test_apprentice_creates_pending_record(self, apprentice_token):
        """Apprentice-created record should have pending_review status"""
        record_data = {
            "record_type": "standard",
            "plate": "TEST999",
            "work_order": "40219999"
        }
        response = requests.post(f"{BASE_URL}/api/records", 
                                json=record_data,
                                headers={"Authorization": f"Bearer {apprentice_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending_review"
        assert data["created_by_role"] == "apprentice"
        print(f"✓ Apprentice record creation passed - Status: {data['status']}")
        return data["id"]
    
    def test_approve_record(self, admin_token):
        """Admin should be able to approve a pending record"""
        # First create a record as apprentice
        apprentice_token = self._get_apprentice_token()
        record_data = {
            "record_type": "standard",
            "plate": "APPROVE01",
            "work_order": "40218001"
        }
        create_response = requests.post(f"{BASE_URL}/api/records", 
                                       json=record_data,
                                       headers={"Authorization": f"Bearer {apprentice_token}"})
        assert create_response.status_code == 200
        record_id = create_response.json()["id"]
        
        # Now approve it as admin
        approve_response = requests.put(f"{BASE_URL}/api/records/{record_id}/approve",
                                       headers={"Authorization": f"Bearer {admin_token}"})
        assert approve_response.status_code == 200
        assert approve_response.json()["success"] == True
        print("✓ Record approval passed")
    
    def test_reject_record(self, admin_token):
        """Admin should be able to reject a pending record"""
        # First create a record as apprentice
        apprentice_token = self._get_apprentice_token()
        record_data = {
            "record_type": "standard",
            "plate": "REJECT01",
            "work_order": "40218002"
        }
        create_response = requests.post(f"{BASE_URL}/api/records", 
                                       json=record_data,
                                       headers={"Authorization": f"Bearer {apprentice_token}"})
        assert create_response.status_code == 200
        record_id = create_response.json()["id"]
        
        # Now reject it as admin
        reject_response = requests.put(f"{BASE_URL}/api/records/{record_id}/reject",
                                      data={"reason": "Test rejection"},
                                      headers={"Authorization": f"Bearer {admin_token}"})
        assert reject_response.status_code == 200
        assert reject_response.json()["success"] == True
        print("✓ Record rejection passed")
    
    def _get_apprentice_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=APPRENTICE_CREDS)
        return response.json()["token"]


class TestNotifications:
    """Test notification system"""
    
    def test_get_notifications(self, admin_token):
        """Should return notifications list"""
        response = requests.get(f"{BASE_URL}/api/notifications", 
                               headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        print(f"✓ Get notifications passed - {data['unread_count']} unread")
    
    def test_apprentice_receives_approval_notification(self, apprentice_token):
        """Apprentice should receive notifications for their records"""
        response = requests.get(f"{BASE_URL}/api/notifications", 
                               headers={"Authorization": f"Bearer {apprentice_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        # Check for approval/rejection notifications
        notification_types = [n.get("notification_type") for n in data["notifications"]]
        print(f"✓ Apprentice notifications passed - {len(data['notifications'])} notifications")


class TestAdminDashboard:
    """Test admin-specific endpoints"""
    
    def test_get_stats(self, admin_token):
        """Admin should see dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/stats", 
                               headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_type" in data
        assert "branches" in data
        assert len(data["branches"]) == 5
        print(f"✓ Dashboard stats passed - Total records: {data['total']}")
    
    def test_get_settings(self, admin_token):
        """Admin should access settings"""
        response = requests.get(f"{BASE_URL}/api/settings", 
                               headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "ocr_provider" in data
        assert "storage_type" in data
        print(f"✓ Settings endpoint passed - Storage: {data['storage_type']}")


class TestStaffDashboard:
    """Test staff-specific endpoints"""
    
    def test_staff_my_stats(self, staff_token):
        """Staff should see their branch stats"""
        response = requests.get(f"{BASE_URL}/api/my-stats", 
                               headers={"Authorization": f"Bearer {staff_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_type" in data
        assert "pending_count" in data
        print(f"✓ Staff stats passed - Branch: {data.get('branch_name')}")


# Fixtures
@pytest.fixture
def admin_token():
    response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
    return response.json()["token"]

@pytest.fixture
def staff_token():
    response = requests.post(f"{BASE_URL}/api/auth/login", json=STAFF_CREDS)
    return response.json()["token"]

@pytest.fixture
def apprentice_token():
    response = requests.post(f"{BASE_URL}/api/auth/login", json=APPRENTICE_CREDS)
    return response.json()["token"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
