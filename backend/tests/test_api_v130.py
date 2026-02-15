"""
Renault Trucks Garanti Kayıt Sistemi - v1.3.0 API Tests
Tests: API version, Service status, Storage providers, Year filtering, Sorting, OCR, Voice-to-Text
"""
import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://truck-service-vault.preview.emergentagent.com')

# Test credentials
ADMIN_CREDS = {"username": "admin", "password": "admin123"}


class TestVersionAndAPIVersion:
    """Test v1.3.0 version and API versioning"""
    
    def test_api_health_check_v130(self):
        """API root should return version 1.3.0"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert data["version"] == "1.3.0"
        print(f"✓ API health check - Version: {data['version']}")
    
    def test_version_endpoint_returns_api_version(self):
        """Version endpoint should return api_version field"""
        response = requests.get(f"{BASE_URL}/api/version")
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields
        assert data["version"] == "1.3.0", f"Expected version 1.3.0, got {data.get('version')}"
        assert data["date"] == "2025-12-15", f"Expected date 2025-12-15, got {data.get('date')}"
        assert "build" in data, "Missing build field"
        assert "fullVersion" in data, "Missing fullVersion field"
        assert "api_version" in data, "Missing api_version field"
        assert data["api_version"] == "v1", f"Expected api_version v1, got {data.get('api_version')}"
        
        print(f"✓ Version endpoint - {data['fullVersion']}, API: {data['api_version']}")


class TestServiceStatus:
    """Test /api/services/status endpoint (admin only)"""
    
    def test_services_status_requires_auth(self):
        """Services status should require authentication"""
        response = requests.get(f"{BASE_URL}/api/services/status")
        assert response.status_code == 401
        print("✓ Services status requires authentication")
    
    def test_services_status_requires_admin(self, staff_token):
        """Services status should require admin role"""
        response = requests.get(
            f"{BASE_URL}/api/services/status",
            headers={"Authorization": f"Bearer {staff_token}"}
        )
        assert response.status_code == 403
        print("✓ Services status requires admin role")
    
    def test_services_status_returns_ocr_voice_storage(self, admin_token):
        """Services status should return OCR, voice, and storage status"""
        response = requests.get(
            f"{BASE_URL}/api/services/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "ocr" in data, "Missing ocr status"
        assert "voice" in data, "Missing voice status"
        assert "storage" in data, "Missing storage status"
        
        # OCR should show configured=False (no API key)
        assert "configured" in data["ocr"]
        assert data["ocr"]["configured"] == False, "OCR should be unconfigured without API key"
        
        # Voice should show configured=False (no API key)
        assert "configured" in data["voice"]
        assert data["voice"]["configured"] == False, "Voice should be unconfigured without API key"
        
        # Storage should show configured=True (local is default)
        assert "configured" in data["storage"]
        assert data["storage"]["configured"] == True, "Storage should be configured (local)"
        assert data["storage"]["provider"] == "local", "Default storage should be local"
        
        print(f"✓ Services status - OCR: {data['ocr']['configured']}, Voice: {data['voice']['configured']}, Storage: {data['storage']['provider']}")


class TestStorageProviders:
    """Test /api/storage/providers endpoint (admin only)"""
    
    def test_storage_providers_requires_auth(self):
        """Storage providers should require authentication"""
        response = requests.get(f"{BASE_URL}/api/storage/providers")
        assert response.status_code == 401
        print("✓ Storage providers requires authentication")
    
    def test_storage_providers_requires_admin(self, staff_token):
        """Storage providers should require admin role"""
        response = requests.get(
            f"{BASE_URL}/api/storage/providers",
            headers={"Authorization": f"Bearer {staff_token}"}
        )
        assert response.status_code == 403
        print("✓ Storage providers requires admin role")
    
    def test_storage_providers_lists_all_providers(self, admin_token):
        """Storage providers should list all available providers"""
        response = requests.get(
            f"{BASE_URL}/api/storage/providers",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "providers" in data, "Missing providers field"
        assert "active" in data, "Missing active provider field"
        
        providers = data["providers"]
        
        # Check all storage providers are listed
        assert "local" in providers, "Missing local provider"
        assert "s3" in providers, "Missing s3 provider"
        assert "gdrive" in providers, "Missing gdrive provider"
        assert "ftp" in providers, "Missing ftp provider"
        assert "onedrive" in providers, "Missing onedrive provider"
        
        # Local should be configured=True, others should be False (no API keys)
        assert providers["local"] == True, "Local storage should be configured"
        assert providers["s3"] == False, "S3 should be unconfigured without API keys"
        assert providers["gdrive"] == False, "Google Drive should be unconfigured without credentials"
        assert providers["ftp"] == False, "FTP should be unconfigured without host/credentials"
        assert providers["onedrive"] == False, "OneDrive should be unconfigured without credentials"
        
        assert data["active"] == "local", "Active provider should be local"
        
        print(f"✓ Storage providers - Active: {data['active']}, Configured: {[k for k, v in providers.items() if v]}")


class TestRecordsYearFilter:
    """Test /api/records year filtering"""
    
    def test_records_with_year_filter(self, admin_token):
        """Records should filter by year parameter"""
        response = requests.get(
            f"{BASE_URL}/api/records?year=2025",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Verify all records are from 2025
        for record in data:
            if "created_at" in record:
                assert record["created_at"].startswith("2025"), f"Record {record['id']} not from 2025"
        
        print(f"✓ Year filter - Found {len(data)} records from 2025")
    
    def test_records_with_year_2024_filter(self, admin_token):
        """Records should return empty/filtered for different year"""
        response = requests.get(
            f"{BASE_URL}/api/records?year=2024",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All records (if any) should be from 2024
        for record in data:
            if "created_at" in record:
                assert record["created_at"].startswith("2024"), f"Record {record['id']} not from 2024"
        
        print(f"✓ Year filter 2024 - Found {len(data)} records")
    
    def test_records_with_future_year_filter(self, admin_token):
        """Records with future year should return empty"""
        response = requests.get(
            f"{BASE_URL}/api/records?year=2030",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0, "Future year should return no records"
        print("✓ Future year filter returns empty list")


class TestRecordsSorting:
    """Test /api/records sorting parameters"""
    
    def test_records_sort_by_created_at_desc(self, admin_token):
        """Records should sort by created_at descending (default)"""
        response = requests.get(
            f"{BASE_URL}/api/records?sort_by=created_at&sort_order=desc",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) >= 2:
            # Verify descending order
            for i in range(len(data) - 1):
                assert data[i]["created_at"] >= data[i+1]["created_at"], "Records not in descending order"
        
        print(f"✓ Sort desc - {len(data)} records in descending order")
    
    def test_records_sort_by_created_at_asc(self, admin_token):
        """Records should sort by created_at ascending"""
        response = requests.get(
            f"{BASE_URL}/api/records?sort_by=created_at&sort_order=asc",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) >= 2:
            # Verify ascending order
            for i in range(len(data) - 1):
                assert data[i]["created_at"] <= data[i+1]["created_at"], "Records not in ascending order"
        
        print(f"✓ Sort asc - {len(data)} records in ascending order")
    
    def test_records_sort_by_plate(self, admin_token):
        """Records should support sorting by plate"""
        response = requests.get(
            f"{BASE_URL}/api/records?sort_by=plate&sort_order=asc",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Sort by plate - {len(data)} records")
    
    def test_records_sort_by_work_order(self, admin_token):
        """Records should support sorting by work_order"""
        response = requests.get(
            f"{BASE_URL}/api/records?sort_by=work_order&sort_order=desc",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Sort by work_order - {len(data)} records")


class TestOCREndpoints:
    """Test OCR endpoints - should return configured=false without API keys"""
    
    def test_ocr_detect_text_requires_auth(self):
        """OCR detect-text should require authentication"""
        # Create a minimal image file
        files = {"file": ("test.jpg", b"fake image data", "image/jpeg")}
        response = requests.post(f"{BASE_URL}/api/ocr/detect-text", files=files)
        assert response.status_code == 401
        print("✓ OCR detect-text requires authentication")
    
    def test_ocr_detect_text_unconfigured(self, admin_token):
        """OCR detect-text should return error when not configured"""
        # Create a minimal test image
        files = {"file": ("test.jpg", b"fake image data", "image/jpeg")}
        response = requests.post(
            f"{BASE_URL}/api/ocr/detect-text",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should indicate OCR is not configured
        assert data.get("success") == False or data.get("use_browser") == True, \
            "OCR should indicate not configured or use browser fallback"
        
        print(f"✓ OCR detect-text returns unconfigured/browser fallback: {data}")
    
    def test_ocr_detect_plate_requires_auth(self):
        """OCR detect-plate should require authentication"""
        files = {"file": ("test.jpg", b"fake image data", "image/jpeg")}
        response = requests.post(f"{BASE_URL}/api/ocr/detect-plate", files=files)
        assert response.status_code == 401
        print("✓ OCR detect-plate requires authentication")
    
    def test_ocr_detect_plate_unconfigured(self, admin_token):
        """OCR detect-plate should return error when not configured"""
        files = {"file": ("test.jpg", b"fake image data", "image/jpeg")}
        response = requests.post(
            f"{BASE_URL}/api/ocr/detect-plate",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should indicate OCR is not configured
        assert data.get("success") == False or data.get("use_browser") == True, \
            "OCR should indicate not configured or use browser fallback"
        
        print(f"✓ OCR detect-plate returns unconfigured/browser fallback: {data}")


class TestVoiceEndpoint:
    """Test Voice-to-Text endpoint - should return configured=false without API keys"""
    
    def test_voice_transcribe_requires_auth(self):
        """Voice transcribe should require authentication"""
        files = {"file": ("test.webm", b"fake audio data", "audio/webm")}
        data = {"language": "tr", "provider": "openai"}
        response = requests.post(f"{BASE_URL}/api/voice/transcribe", files=files, data=data)
        assert response.status_code == 401
        print("✓ Voice transcribe requires authentication")
    
    def test_voice_transcribe_unconfigured(self, admin_token):
        """Voice transcribe should return error when not configured"""
        files = {"file": ("test.webm", b"fake audio data", "audio/webm")}
        data = {"language": "tr", "provider": "openai"}
        response = requests.post(
            f"{BASE_URL}/api/voice/transcribe",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        result = response.json()
        
        # Should indicate voice service is not configured
        assert result.get("success") == False or result.get("use_browser") == True, \
            "Voice should indicate not configured or use browser fallback"
        
        print(f"✓ Voice transcribe returns unconfigured/browser fallback: {result}")


class TestRecordsCombinedFilters:
    """Test records with combined filter and sort parameters"""
    
    def test_records_year_and_sort_combined(self, admin_token):
        """Records should support year filter + sorting together"""
        response = requests.get(
            f"{BASE_URL}/api/records?year=2025&sort_by=created_at&sort_order=desc",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Verify all from 2025 and in descending order
        for record in data:
            if "created_at" in record:
                assert record["created_at"].startswith("2025")
        
        if len(data) >= 2:
            for i in range(len(data) - 1):
                assert data[i]["created_at"] >= data[i+1]["created_at"]
        
        print(f"✓ Combined year+sort filter - {len(data)} records")
    
    def test_records_type_year_sort_combined(self, admin_token):
        """Records should support record_type + year + sorting together"""
        response = requests.get(
            f"{BASE_URL}/api/records?record_type=standard&year=2025&sort_by=created_at&sort_order=desc",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Verify all are standard type from 2025
        for record in data:
            assert record["record_type"] == "standard"
            if "created_at" in record:
                assert record["created_at"].startswith("2025")
        
        print(f"✓ Combined type+year+sort filter - {len(data)} standard records from 2025")


# Fixtures
@pytest.fixture
def admin_token():
    response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
    if response.status_code != 200:
        pytest.skip("Admin login failed - skipping authenticated tests")
    return response.json()["token"]


@pytest.fixture
def staff_token():
    # Use existing staff from previous tests
    staff_creds = {"username": "hadimkoy_garanti", "password": "test123"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=staff_creds)
    if response.status_code != 200:
        pytest.skip("Staff login failed - skipping staff tests")
    return response.json()["token"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
