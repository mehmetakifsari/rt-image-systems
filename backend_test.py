#!/usr/bin/env python3

import requests
import sys
import os
import json
from datetime import datetime
import io

class RenaultTrucksAPITester:
    def __init__(self, base_url="https://bana-proje.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.admin_token = None
        self.test_record_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = {
            "passed": [],
            "failed": [],
            "summary": {}
        }

    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            self.test_results["passed"].append(test_name)
            print(f"✅ {test_name}")
        else:
            self.test_results["failed"].append({"test": test_name, "details": details})
            print(f"❌ {test_name}: {details}")

    def test_api_health(self):
        """Test API health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "Renault Trucks" in data.get("message", ""):
                    self.log_result("API Health Check", True)
                    return True
                else:
                    self.log_result("API Health Check", False, "Invalid response message")
                    return False
            else:
                self.log_result("API Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("API Health Check", False, str(e))
            return False

    def test_admin_login(self):
        """Test admin login with admin/admin123"""
        try:
            data = {"username": "admin", "password": "admin123"}
            response = requests.post(f"{self.base_url}/auth/login", json=data)
            
            if response.status_code == 200:
                result = response.json()
                if "token" in result and "user" in result:
                    self.admin_token = result["token"]
                    user = result["user"]
                    if user.get("role") == "admin":
                        self.log_result("Admin Login", True)
                        return True
                    else:
                        self.log_result("Admin Login", False, "User role is not admin")
                        return False
                else:
                    self.log_result("Admin Login", False, "Missing token or user in response")
                    return False
            else:
                self.log_result("Admin Login", False, f"Status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result("Admin Login", False, str(e))
            return False

    def test_auth_me(self):
        """Test get current user info"""
        if not self.admin_token:
            self.log_result("Get Current User", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user = response.json()
                if user.get("username") == "admin" and user.get("role") == "admin":
                    self.log_result("Get Current User", True)
                    return True
                else:
                    self.log_result("Get Current User", False, "Invalid user data")
                    return False
            else:
                self.log_result("Get Current User", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Get Current User", False, str(e))
            return False

    def test_create_standard_record(self):
        """Test creating a Standard record"""
        if not self.admin_token:
            self.log_result("Create Standard Record", False, "No admin token")
            return False
            
        try:
            data = {
                "record_type": "standard",
                "plate": "34TEST123",
                "work_order": "WO-2024-001",
                "note_text": "Test standard record"
            }
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/records", json=data, headers=headers)
            
            if response.status_code == 200:
                record = response.json()
                if record.get("record_type") == "standard" and record.get("plate") == "34TEST123":
                    self.test_record_id = record.get("id")
                    self.log_result("Create Standard Record", True)
                    return True
                else:
                    self.log_result("Create Standard Record", False, "Invalid record data")
                    return False
            else:
                self.log_result("Create Standard Record", False, f"Status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result("Create Standard Record", False, str(e))
            return False

    def test_create_roadassist_record(self):
        """Test creating a RoadAssist record"""
        if not self.admin_token:
            self.log_result("Create RoadAssist Record", False, "No admin token")
            return False
            
        try:
            data = {
                "record_type": "roadassist",
                "plate": "06HELP456"
            }
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/records", json=data, headers=headers)
            
            if response.status_code == 200:
                record = response.json()
                if record.get("record_type") == "roadassist" and record.get("plate") == "06HELP456":
                    self.log_result("Create RoadAssist Record", True)
                    return True
                else:
                    self.log_result("Create RoadAssist Record", False, "Invalid record data")
                    return False
            else:
                self.log_result("Create RoadAssist Record", False, f"Status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result("Create RoadAssist Record", False, str(e))
            return False

    def test_create_damaged_record(self):
        """Test creating a Damaged record"""
        if not self.admin_token:
            self.log_result("Create Damaged Record", False, "No admin token")
            return False
            
        try:
            data = {
                "record_type": "damaged",
                "reference_no": "DMG-2024-001"
            }
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/records", json=data, headers=headers)
            
            if response.status_code == 200:
                record = response.json()
                if record.get("record_type") == "damaged" and record.get("reference_no") == "DMG-2024-001":
                    self.log_result("Create Damaged Record", True)
                    return True
                else:
                    self.log_result("Create Damaged Record", False, "Invalid record data")
                    return False
            else:
                self.log_result("Create Damaged Record", False, f"Status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result("Create Damaged Record", False, str(e))
            return False

    def test_create_pdi_record(self):
        """Test creating a PDI record"""
        if not self.admin_token:
            self.log_result("Create PDI Record", False, "No admin token")
            return False
            
        try:
            data = {
                "record_type": "pdi",
                "vin": "VF1TESTVIN1234567"
            }
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/records", json=data, headers=headers)
            
            if response.status_code == 200:
                record = response.json()
                if record.get("record_type") == "pdi" and record.get("vin") == "VF1TESTVIN1234567":
                    self.log_result("Create PDI Record", True)
                    return True
                else:
                    self.log_result("Create PDI Record", False, "Invalid record data")
                    return False
            else:
                self.log_result("Create PDI Record", False, f"Status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result("Create PDI Record", False, str(e))
            return False

    def test_get_records_list(self):
        """Test getting records list"""
        if not self.admin_token:
            self.log_result("Get Records List", False, "No admin token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/records", headers=headers)
            
            if response.status_code == 200:
                records = response.json()
                if isinstance(records, list) and len(records) > 0:
                    self.log_result("Get Records List", True)
                    return True
                else:
                    self.log_result("Get Records List", False, "Empty or invalid records list")
                    return False
            else:
                self.log_result("Get Records List", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Get Records List", False, str(e))
            return False

    def test_get_single_record(self):
        """Test getting a single record by ID"""
        if not self.admin_token or not self.test_record_id:
            self.log_result("Get Single Record", False, "Missing admin token or record ID")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/records/{self.test_record_id}", headers=headers)
            
            if response.status_code == 200:
                record = response.json()
                if record.get("id") == self.test_record_id and record.get("record_type") == "standard":
                    self.log_result("Get Single Record", True)
                    return True
                else:
                    self.log_result("Get Single Record", False, "Invalid record data")
                    return False
            else:
                self.log_result("Get Single Record", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Get Single Record", False, str(e))
            return False

    def test_update_record_note(self):
        """Test updating record note"""
        if not self.admin_token or not self.test_record_id:
            self.log_result("Update Record Note", False, "Missing admin token or record ID")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            data = {"note_text": "Updated test note via API"}
            response = requests.put(f"{self.base_url}/records/{self.test_record_id}/note", data=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("Update Record Note", True)
                    return True
                else:
                    self.log_result("Update Record Note", False, "Success not returned")
                    return False
            else:
                self.log_result("Update Record Note", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Update Record Note", False, str(e))
            return False

    def test_file_upload(self):
        """Test file upload functionality"""
        if not self.admin_token or not self.test_record_id:
            self.log_result("File Upload", False, "Missing admin token or record ID")
            return False
            
        try:
            # Create a small test image file
            test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            files = {"file": ("test.png", io.BytesIO(test_image_data), "image/png")}
            data = {"media_type": "photo"}
            
            response = requests.post(f"{self.base_url}/records/{self.test_record_id}/upload", 
                                   files=files, data=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and "file" in result:
                    self.log_result("File Upload", True)
                    return True
                else:
                    self.log_result("File Upload", False, "Invalid upload response")
                    return False
            else:
                self.log_result("File Upload", False, f"Status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result("File Upload", False, str(e))
            return False

    def test_get_stats(self):
        """Test admin dashboard statistics"""
        if not self.admin_token:
            self.log_result("Get Dashboard Stats", False, "No admin token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/stats", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                expected_keys = ["total", "by_type", "recent"]
                if all(key in stats for key in expected_keys):
                    if "standard" in stats["by_type"]:
                        self.log_result("Get Dashboard Stats", True)
                        return True
                    else:
                        self.log_result("Get Dashboard Stats", False, "Missing record types in stats")
                        return False
                else:
                    self.log_result("Get Dashboard Stats", False, "Missing expected keys in stats")
                    return False
            else:
                self.log_result("Get Dashboard Stats", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Get Dashboard Stats", False, str(e))
            return False

    def test_get_settings(self):
        """Test getting admin settings"""
        if not self.admin_token:
            self.log_result("Get Admin Settings", False, "No admin token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/settings", headers=headers)
            
            if response.status_code == 200:
                settings = response.json()
                expected_keys = ["ocr_provider", "storage_type", "language"]
                if all(key in settings for key in expected_keys):
                    self.log_result("Get Admin Settings", True)
                    return True
                else:
                    self.log_result("Get Admin Settings", False, "Missing expected settings keys")
                    return False
            else:
                self.log_result("Get Admin Settings", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Get Admin Settings", False, str(e))
            return False

    def test_update_settings(self):
        """Test updating admin settings"""
        if not self.admin_token:
            self.log_result("Update Admin Settings", False, "No admin token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            data = {
                "ocr_provider": "browser",
                "storage_type": "local",
                "language": "tr"
            }
            response = requests.put(f"{self.base_url}/settings", json=data, headers=headers)
            
            if response.status_code == 200:
                settings = response.json()
                if (settings.get("ocr_provider") == "browser" and 
                    settings.get("storage_type") == "local"):
                    self.log_result("Update Admin Settings", True)
                    return True
                else:
                    self.log_result("Update Admin Settings", False, "Settings not updated correctly")
                    return False
            else:
                self.log_result("Update Admin Settings", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Update Admin Settings", False, str(e))
            return False

    def test_search_records(self):
        """Test record search functionality"""
        if not self.admin_token:
            self.log_result("Search Records", False, "No admin token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            # Search by plate number
            response = requests.get(f"{self.base_url}/records?search=34TEST", headers=headers)
            
            if response.status_code == 200:
                records = response.json()
                if isinstance(records, list):
                    # Check if search worked - should find our test record
                    found_record = any(r.get("plate") == "34TEST123" for r in records)
                    if found_record:
                        self.log_result("Search Records", True)
                        return True
                    else:
                        self.log_result("Search Records", False, "Search didn't find expected record")
                        return False
                else:
                    self.log_result("Search Records", False, "Invalid search response format")
                    return False
            else:
                self.log_result("Search Records", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Search Records", False, str(e))
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print(f"🚛 Starting Renault Trucks API Tests")
        print(f"📡 Testing: {self.base_url}")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_api_health():
            print("❌ API is not accessible. Stopping tests.")
            return False
            
        # Authentication tests
        if not self.test_admin_login():
            print("❌ Cannot login as admin. Stopping tests.")
            return False
            
        self.test_auth_me()
        
        # Record CRUD tests
        self.test_create_standard_record()
        self.test_create_roadassist_record()
        self.test_create_damaged_record()
        self.test_create_pdi_record()
        
        # Data retrieval tests
        self.test_get_records_list()
        self.test_get_single_record()
        self.test_search_records()
        
        # Update operations
        self.test_update_record_note()
        self.test_file_upload()
        
        # Admin features
        self.test_get_stats()
        self.test_get_settings()
        self.test_update_settings()
        
        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.test_results["failed"]:
            print("\n❌ Failed Tests:")
            for failure in self.test_results["failed"]:
                print(f"   • {failure['test']}: {failure['details']}")
        
        if self.test_results["passed"]:
            print("\n✅ Passed Tests:")
            for test in self.test_results["passed"]:
                print(f"   • {test}")
        
        # Summary
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.test_results["summary"] = {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": len(self.test_results["failed"]),
            "success_rate": f"{success_rate:.1f}%"
        }
        
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        return self.tests_passed == self.tests_run

def main():
    tester = RenaultTrucksAPITester()
    success = tester.run_all_tests()
    
    # Save results to file for testing agent
    with open("/app/backend_test_results.json", "w") as f:
        json.dump(tester.test_results, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())