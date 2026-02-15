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
        self.staff_token = None
        self.test_record_id = None
        self.test_staff_id = None
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
                "plate": "06HELP456",
                "branch_code": "4"  # Required for RoadAssist records
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
                "reference_no": "DMG-2024-001",
                "branch_code": "4"  # Required for Damaged records
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
                "vin": "VF1TESTVIN1234567",
                "branch_code": "4"  # Required for PDI records
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

    def test_staff_login(self):
        """Test staff login with hadimkoy_garanti/test123"""
        try:
            data = {"username": "hadimkoy_garanti", "password": "test123"}
            response = requests.post(f"{self.base_url}/auth/login", json=data)
            
            if response.status_code == 200:
                result = response.json()
                if "token" in result and "user" in result:
                    self.staff_token = result["token"]
                    user = result["user"]
                    if user.get("role") == "staff" and user.get("branch_code") == "4":
                        self.log_result("Staff Login", True)
                        return True
                    else:
                        self.log_result("Staff Login", False, f"Expected staff role and branch 4, got role: {user.get('role')}, branch: {user.get('branch_code')}")
                        return False
                else:
                    self.log_result("Staff Login", False, "Missing token or user in response")
                    return False
            else:
                self.log_result("Staff Login", False, f"Status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result("Staff Login", False, str(e))
            return False

    def test_branches_endpoint(self):
        """Test getting branches list"""
        try:
            response = requests.get(f"{self.base_url}/branches")
            
            if response.status_code == 200:
                result = response.json()
                branches = result.get("branches", [])
                if len(branches) == 5:
                    expected_branches = {
                        "1": "Bursa", "2": "İzmit", "3": "Orhanlı", 
                        "4": "Hadımköy", "5": "Keşan"
                    }
                    for branch in branches:
                        code = branch.get("code")
                        name = branch.get("name")
                        if code not in expected_branches or expected_branches[code] != name:
                            self.log_result("Get Branches", False, f"Invalid branch data: {branch}")
                            return False
                    self.log_result("Get Branches", True)
                    return True
                else:
                    self.log_result("Get Branches", False, f"Expected 5 branches, got {len(branches)}")
                    return False
            else:
                self.log_result("Get Branches", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Get Branches", False, str(e))
            return False

    def test_create_staff_user(self):
        """Test admin creating a staff user"""
        if not self.admin_token:
            self.log_result("Create Staff User", False, "No admin token")
            return False
            
        try:
            data = {
                "username": "test_staff_user",
                "password": "testpass123",
                "full_name": "Test Staff User",
                "role": "staff",
                "branch_code": "4",
                "job_title": "garanti_danisman",
                "phone": "+905551234567",
                "whatsapp": "905551234567"
            }
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/auth/register", json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if (result.get("username") == "test_staff_user" and 
                    result.get("role") == "staff" and 
                    result.get("branch_code") == "4"):
                    self.test_staff_id = result.get("id")
                    self.log_result("Create Staff User", True)
                    return True
                else:
                    self.log_result("Create Staff User", False, "Invalid staff user data")
                    return False
            else:
                self.log_result("Create Staff User", False, f"Status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result("Create Staff User", False, str(e))
            return False

    def test_get_staff_list(self):
        """Test admin getting staff list"""
        if not self.admin_token:
            self.log_result("Get Staff List", False, "No admin token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/staff", headers=headers)
            
            if response.status_code == 200:
                staff_list = response.json()
                if isinstance(staff_list, list):
                    self.log_result("Get Staff List", True)
                    return True
                else:
                    self.log_result("Get Staff List", False, "Invalid staff list response")
                    return False
            else:
                self.log_result("Get Staff List", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Get Staff List", False, str(e))
            return False

    def test_staff_branch_filtering(self):
        """Test admin getting staff filtered by branch"""
        if not self.admin_token:
            self.log_result("Staff Branch Filtering", False, "No admin token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/staff?branch_code=4", headers=headers)
            
            if response.status_code == 200:
                staff_list = response.json()
                if isinstance(staff_list, list):
                    # All returned staff should be from branch 4
                    all_branch_4 = all(s.get("branch_code") == "4" for s in staff_list)
                    if all_branch_4:
                        self.log_result("Staff Branch Filtering", True)
                        return True
                    else:
                        self.log_result("Staff Branch Filtering", False, "Staff from other branches returned")
                        return False
                else:
                    self.log_result("Staff Branch Filtering", False, "Invalid staff list response")
                    return False
            else:
                self.log_result("Staff Branch Filtering", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Staff Branch Filtering", False, str(e))
            return False

    def test_work_order_branch_extraction(self):
        """Test work order branch code extraction"""
        if not self.admin_token:
            self.log_result("Work Order Branch Extraction", False, "No admin token")
            return False
            
        try:
            data = {
                "record_type": "standard",
                "plate": "34TEST456",
                "work_order": "40216001",  # Should extract branch code 4
                "note_text": "Test work order branch extraction"
            }
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/records", json=data, headers=headers)
            
            if response.status_code == 200:
                record = response.json()
                if record.get("branch_code") == "4":
                    self.log_result("Work Order Branch Extraction", True)
                    return True
                else:
                    self.log_result("Work Order Branch Extraction", False, f"Expected branch code 4, got {record.get('branch_code')}")
                    return False
            else:
                self.log_result("Work Order Branch Extraction", False, f"Status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result("Work Order Branch Extraction", False, str(e))
            return False

    def test_branch_selection_required(self):
        """Test branch selection requirement for PDI/Damaged/RoadAssist records"""
        if not self.admin_token:
            self.log_result("Branch Selection Required", False, "No admin token")
            return False
            
        try:
            # Test PDI record without branch - should fail
            data = {
                "record_type": "pdi",
                "vin": "VF1TESTVIN9876543"
                # No branch_code provided
            }
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/records", json=data, headers=headers)
            
            if response.status_code == 400:
                error_detail = response.json().get("detail", "")
                if "şube" in error_detail.lower():
                    self.log_result("Branch Selection Required", True)
                    return True
                else:
                    self.log_result("Branch Selection Required", False, "Wrong error message")
                    return False
            else:
                self.log_result("Branch Selection Required", False, f"Expected 400 error, got {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Branch Selection Required", False, str(e))
            return False

    def test_staff_record_restriction(self):
        """Test that staff can only see their branch records"""
        if not self.staff_token:
            # Try to create a staff token first
            if not self.test_staff_login():
                self.log_result("Staff Record Restriction", False, "No staff token available")
                return False
            
        try:
            headers = {"Authorization": f"Bearer {self.staff_token}"}
            response = requests.get(f"{self.base_url}/records", headers=headers)
            
            if response.status_code == 200:
                records = response.json()
                if isinstance(records, list):
                    # All records should be from branch 4 (Hadımköy)
                    if records:  # If there are records
                        all_branch_4 = all(r.get("branch_code") == "4" for r in records)
                        if all_branch_4:
                            self.log_result("Staff Record Restriction", True)
                            return True
                        else:
                            self.log_result("Staff Record Restriction", False, "Staff can see records from other branches")
                            return False
                    else:
                        # If no records, that's also valid - staff might not have any records yet
                        self.log_result("Staff Record Restriction", True)
                        return True
                else:
                    self.log_result("Staff Record Restriction", False, "Invalid records response")
                    return False
            else:
                self.log_result("Staff Record Restriction", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Staff Record Restriction", False, str(e))
            return False

    def test_admin_dashboard_branches(self):
        """Test admin dashboard shows all branches"""
        if not self.admin_token:
            self.log_result("Admin Dashboard Branches", False, "No admin token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/stats", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                branches = stats.get("branches", [])
                if len(branches) == 5:
                    # Check that all expected branches are present
                    branch_codes = [b.get("code") for b in branches]
                    expected_codes = ["1", "2", "3", "4", "5"]
                    if all(code in branch_codes for code in expected_codes):
                        self.log_result("Admin Dashboard Branches", True)
                        return True
                    else:
                        self.log_result("Admin Dashboard Branches", False, f"Missing branch codes: {expected_codes} vs {branch_codes}")
                        return False
                else:
                    self.log_result("Admin Dashboard Branches", False, f"Expected 5 branches in dashboard, got {len(branches)}")
                    return False
            else:
                self.log_result("Admin Dashboard Branches", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Admin Dashboard Branches", False, str(e))
            return False

    def test_delete_staff_user(self):
        """Test admin deleting a staff user"""
        if not self.admin_token or not self.test_staff_id:
            self.log_result("Delete Staff User", False, "No admin token or staff ID")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.delete(f"{self.base_url}/staff/{self.test_staff_id}", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("Delete Staff User", True)
                    return True
                else:
                    self.log_result("Delete Staff User", False, "Success not returned")
                    return False
            else:
                self.log_result("Delete Staff User", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Delete Staff User", False, str(e))
            return False

    def test_logout_functionality(self):
        """Test logout functionality"""
        if not self.admin_token:
            self.log_result("Logout Functionality", False, "No admin token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/auth/logout", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("Logout Functionality", True)
                    return True
                else:
                    self.log_result("Logout Functionality", False, "Success not returned")
                    return False
            else:
                self.log_result("Logout Functionality", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Logout Functionality", False, str(e))
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
        
        # Test branches endpoint (no auth required)
        self.test_branches_endpoint()
            
        # Authentication tests
        if not self.test_admin_login():
            print("❌ Cannot login as admin. Stopping tests.")
            return False
            
        self.test_auth_me()
        
        # Test staff login
        self.test_staff_login()
        
        # Admin dashboard and branch management
        self.test_admin_dashboard_branches()
        
        # Staff management tests
        self.test_create_staff_user()
        self.test_get_staff_list()
        self.test_staff_branch_filtering()
        
        # Record creation tests with branch system
        self.test_create_standard_record()
        self.test_work_order_branch_extraction()
        self.test_branch_selection_required()
        self.test_create_roadassist_record()
        self.test_create_damaged_record()
        self.test_create_pdi_record()
        
        # Data retrieval and filtering tests
        self.test_get_records_list()
        self.test_get_single_record()
        self.test_staff_record_restriction()
        
        # Update operations
        self.test_update_record_note()
        self.test_file_upload()
        
        # Admin features
        self.test_get_stats()
        self.test_get_settings()
        self.test_update_settings()
        
        # Cleanup tests
        self.test_delete_staff_user()
        self.test_logout_functionality()
        
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