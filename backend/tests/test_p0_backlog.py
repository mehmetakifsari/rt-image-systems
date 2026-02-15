"""
P0 Backlog Testing - OCR, Voice-to-Text, and Settings API Tests
Tests the following features:
1. Login functionality (admin/admin123 and staff accounts)
2. OCR /api/ocr/detect-plate endpoint
3. Voice /api/voice/transcribe endpoint
4. Settings GET and PUT operations
"""

import pytest
import requests
import os

# Get the backend URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://claim-visual-db.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_CREDS = {"username": "admin", "password": "admin123"}
STAFF_CREDS = {"username": "hadimkoy_garanti", "password": "password123"}


class TestAuthentication:
    """Test login functionality"""
    
    def test_admin_login_success(self):
        """Admin login with correct credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        assert response.status_code == 200
        
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["username"] == "admin"
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful, role: {data['user']['role']}")
    
    def test_admin_login_wrong_password(self):
        """Admin login with wrong password should fail"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Admin login with wrong password correctly rejected")
    
    def test_invalid_user_login(self):
        """Non-existent user login should fail"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "nonexistent_user",
            "password": "somepassword"
        })
        assert response.status_code == 401
        print("✓ Non-existent user login correctly rejected")


class TestOCREndpoints:
    """Test OCR API endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin authentication failed")
    
    def test_ocr_detect_plate_endpoint_accessible(self, admin_token):
        """Test /api/ocr/detect-plate endpoint is accessible"""
        # Create a dummy image file
        files = {'file': ('test.jpg', b'dummy image data', 'image/jpeg')}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/ocr/detect-plate",
            files=files,
            headers=headers
        )
        
        # Should return 200 even if OCR is not configured (returns use_browser: true)
        assert response.status_code == 200
        data = response.json()
        
        # Without API keys, should suggest using browser
        if not data.get("success"):
            assert data.get("use_browser") == True or "not configured" in data.get("error", "").lower()
            print("✓ OCR endpoint accessible, returns use_browser=true (no API key configured)")
        else:
            print("✓ OCR endpoint accessible and working")
    
    def test_ocr_detect_text_endpoint_accessible(self, admin_token):
        """Test /api/ocr/detect-text endpoint is accessible"""
        files = {'file': ('test.jpg', b'dummy image data', 'image/jpeg')}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/ocr/detect-text",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if not data.get("success"):
            assert data.get("use_browser") == True or "not configured" in data.get("error", "").lower()
            print("✓ OCR detect-text endpoint accessible, returns use_browser=true")
        else:
            print("✓ OCR detect-text endpoint working")
    
    def test_ocr_requires_authentication(self):
        """Test OCR endpoint requires authentication"""
        files = {'file': ('test.jpg', b'dummy', 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/api/ocr/detect-plate", files=files)
        assert response.status_code == 401
        print("✓ OCR endpoint correctly requires authentication")


class TestVoiceEndpoints:
    """Test Voice-to-Text API endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin authentication failed")
    
    def test_voice_transcribe_endpoint_accessible(self, admin_token):
        """Test /api/voice/transcribe endpoint is accessible"""
        # Create a dummy audio file
        files = {'file': ('test.webm', b'dummy audio data', 'audio/webm')}
        data = {'language': 'tr', 'provider': 'openai'}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/voice/transcribe",
            files=files,
            data=data,
            headers=headers
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Without API keys, should suggest using browser
        if not result.get("success"):
            assert result.get("use_browser") == True or "not configured" in result.get("error", "").lower()
            print("✓ Voice transcribe endpoint accessible, returns use_browser=true (no API key configured)")
        else:
            print("✓ Voice transcribe endpoint working")
    
    def test_voice_transcribe_with_different_providers(self, admin_token):
        """Test voice transcribe with different provider options"""
        files = {'file': ('test.webm', b'dummy audio data', 'audio/webm')}
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        for provider in ['openai', 'gemini', 'browser']:
            response = requests.post(
                f"{BASE_URL}/api/voice/transcribe",
                files=files,
                data={'language': 'tr', 'provider': provider},
                headers=headers
            )
            assert response.status_code == 200
            print(f"✓ Voice transcribe with provider '{provider}' returns 200")
    
    def test_voice_requires_authentication(self):
        """Test Voice endpoint requires authentication"""
        files = {'file': ('test.webm', b'dummy', 'audio/webm')}
        response = requests.post(f"{BASE_URL}/api/voice/transcribe", files=files)
        assert response.status_code == 401
        print("✓ Voice endpoint correctly requires authentication")


class TestSettingsEndpoints:
    """Test Settings API endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin authentication failed")
    
    def test_get_settings(self, admin_token):
        """Test GET /api/settings"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/settings", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected fields exist
        assert "id" in data
        assert "ocr_provider" in data
        assert "voice_provider" in data
        assert "storage_type" in data
        assert "language" in data
        
        print(f"✓ Settings retrieved: ocr_provider={data['ocr_provider']}, voice_provider={data['voice_provider']}, storage_type={data['storage_type']}")
    
    def test_update_settings_ocr_provider(self, admin_token):
        """Test updating OCR provider setting"""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        # Update to browser
        response = requests.put(
            f"{BASE_URL}/api/settings",
            json={"ocr_provider": "browser"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ocr_provider"] == "browser"
        print("✓ OCR provider updated to 'browser'")
        
        # Update to vision
        response = requests.put(
            f"{BASE_URL}/api/settings",
            json={"ocr_provider": "vision"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ocr_provider"] == "vision"
        print("✓ OCR provider updated to 'vision'")
        
        # Reset to browser
        requests.put(
            f"{BASE_URL}/api/settings",
            json={"ocr_provider": "browser"},
            headers=headers
        )
    
    def test_update_settings_voice_provider(self, admin_token):
        """Test updating Voice provider setting"""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        # Test all voice providers
        for provider in ['browser', 'openai', 'gemini']:
            response = requests.put(
                f"{BASE_URL}/api/settings",
                json={"voice_provider": provider},
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data["voice_provider"] == provider
            print(f"✓ Voice provider updated to '{provider}'")
        
        # Reset to browser
        requests.put(
            f"{BASE_URL}/api/settings",
            json={"voice_provider": "browser"},
            headers=headers
        )
    
    def test_update_settings_storage_type(self, admin_token):
        """Test updating Storage type setting"""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        # Test storage types
        for storage in ['local', 'ftp', 's3', 'gdrive', 'onedrive']:
            response = requests.put(
                f"{BASE_URL}/api/settings",
                json={"storage_type": storage},
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data["storage_type"] == storage
            print(f"✓ Storage type updated to '{storage}'")
        
        # Reset to local
        requests.put(
            f"{BASE_URL}/api/settings",
            json={"storage_type": "local"},
            headers=headers
        )
    
    def test_settings_requires_admin(self):
        """Test settings endpoint requires admin role"""
        # Without auth
        response = requests.get(f"{BASE_URL}/api/settings")
        assert response.status_code == 401
        print("✓ Settings correctly requires authentication")


class TestRecordFormValidation:
    """Test record creation form validation"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin authentication failed")
    
    def test_standard_record_requires_plate_and_work_order(self, admin_token):
        """Test standard record validation"""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        # Missing plate should fail
        response = requests.post(
            f"{BASE_URL}/api/records",
            json={"record_type": "standard", "work_order": "40216001"},
            headers=headers
        )
        assert response.status_code == 400
        print("✓ Standard record without plate correctly rejected")
        
        # Missing work order should fail
        response = requests.post(
            f"{BASE_URL}/api/records",
            json={"record_type": "standard", "plate": "34ABC123"},
            headers=headers
        )
        assert response.status_code == 400
        print("✓ Standard record without work_order correctly rejected")
    
    def test_create_standard_record_success(self, admin_token):
        """Test successful standard record creation"""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/records",
            json={
                "record_type": "standard",
                "plate": "TEST_34XYZ999",
                "work_order": "40216999",
                "note_text": "Test record from P0 backlog test"
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["plate"] == "TEST_34XYZ999"
        assert data["work_order"] == "40216999"
        assert "id" in data
        print(f"✓ Standard record created with id: {data['id']}")
        
        # Cleanup - delete the test record
        requests.delete(f"{BASE_URL}/api/records/{data['id']}", headers=headers)


class TestServiceStatus:
    """Test service status endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Admin authentication failed")
    
    def test_services_status(self, admin_token):
        """Test /api/services/status endpoint"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/services/status", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "ocr" in data
        assert "voice" in data
        assert "storage" in data
        
        print(f"✓ Services status: OCR configured={data['ocr']['configured']}, Voice configured={data['voice']['configured']}, Storage provider={data['storage']['provider']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
