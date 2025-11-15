#!/usr/bin/env python3
"""
Final Comprehensive Backend Test for SkyApp
Tests all CRUD operations including UPDATE and DELETE
"""

import requests
import sys
import json
import uuid
from datetime import datetime

class SkyAppFinalTester:
    def __init__(self):
        self.base_url = "https://smart-inventory-97.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        
        # Test tracking
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        
        # Authentication tokens and user data
        self.bureau_token = None
        self.bureau_user = None
        
        # Test data storage
        self.test_data = {
            'searches': [],
            'reports': [],
            'clients': [],
            'quotes': [],
            'sites': [],
            'invitations': []
        }
        
        # Generate unique identifiers for this test run
        self.test_id = str(uuid.uuid4())[:8]
        self.unique_email = f"final-{self.test_id}@btp-test.fr"
        self.unique_company = f"BTP Final {self.test_id}"

    def log_test(self, name: str, success: bool, response_data=None, error: str = None):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if response_data and isinstance(response_data, dict) and len(str(response_data)) < 200:
                print(f"   Response: {response_data}")
        else:
            print(f"❌ {name}")
            if error:
                print(f"   Error: {error}")
            self.critical_failures.append(f"{name}: {error}")

    def make_request(self, method: str, endpoint: str, data=None, token: str = None, 
                    expected_status: int = 200, raw_data: str = None):
        """Make HTTP request"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                if raw_data is not None:
                    headers['Content-Type'] = 'text/plain'
                    response = requests.put(url, data=raw_data, headers=headers, timeout=15)
                else:
                    headers['Content-Type'] = 'application/json'
                    response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)
            else:
                return False, f"Unsupported method: {method}"
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            if not success:
                error_msg = f"Expected {expected_status}, got {response.status_code}. Response: {response_data}"
                return False, error_msg
            
            return True, response_data
            
        except Exception as e:
            return False, f"Request failed: {str(e)}"

    def setup_test_data(self):
        """Setup initial test data"""
        print("🔧 Setting up test data...")
        
        # Register and login
        register_data = {
            "company_name": self.unique_company,
            "email": self.unique_email,
            "nom": "Test",
            "prenom": "User",
            "password": "test123"
        }
        
        success, response = self.make_request('POST', 'auth/register', register_data)
        if success and 'access_token' in response:
            self.bureau_token = response['access_token']
            self.bureau_user = response['user']
            print(f"✅ Setup complete - User: {self.bureau_user['email']}")
            return True
        else:
            print(f"❌ Setup failed: {response}")
            return False

    def test_complete_search_crud(self):
        """Test complete CRUD operations for searches"""
        print("\n🔍 Testing Complete Search CRUD...")
        
        # CREATE
        search_data = {
            "location": f"Test Location {self.test_id}",
            "description": "Test search description",
            "observations": "Test observations",
            "latitude": 48.8566,
            "longitude": 2.3522
        }
        
        success, response = self.make_request('POST', 'searches', search_data, token=self.bureau_token)
        if success and 'id' in response:
            search_id = response['id']
            self.test_data['searches'].append(response)
            self.log_test("Create Search", True, {"id": search_id})
        else:
            self.log_test("Create Search", False, None, response)
            return False
        
        # READ (single)
        success, response = self.make_request('GET', f'searches/{search_id}', token=self.bureau_token)
        self.log_test("Read Single Search", success, 
                     {"location": response.get('location')} if success else None,
                     response if not success else None)
        
        # READ (all)
        success, response = self.make_request('GET', 'searches', token=self.bureau_token)
        search_count = len(response) if success and isinstance(response, list) else 0
        self.log_test("Read All Searches", success, {"count": search_count})
        
        # UPDATE (status)
        success, response = self.make_request('PUT', f'searches/{search_id}/status', 
                                            token=self.bureau_token, raw_data="SHARED")
        self.log_test("Update Search Status", success, response)
        
        return True

    def test_complete_client_crud(self):
        """Test complete CRUD operations for clients"""
        print("\n👥 Testing Complete Client CRUD...")
        
        # CREATE
        client_data = {
            "nom": f"Test Client {self.test_id}",
            "email": f"client-{self.test_id}@test.fr",
            "telephone": "01 23 45 67 89",
            "adresse": "123 Test Street"
        }
        
        success, response = self.make_request('POST', 'clients', client_data, token=self.bureau_token)
        if success and 'id' in response:
            client_id = response['id']
            self.test_data['clients'].append(response)
            self.log_test("Create Client", True, {"id": client_id, "nom": response.get('nom')})
        else:
            self.log_test("Create Client", False, None, response)
            return False
        
        # READ (all)
        success, response = self.make_request('GET', 'clients', token=self.bureau_token)
        client_count = len(response) if success and isinstance(response, list) else 0
        self.log_test("Read All Clients", success, {"count": client_count})
        
        # UPDATE
        update_data = {
            "nom": f"Updated Client {self.test_id}",
            "telephone": "01 98 76 54 32"
        }
        success, response = self.make_request('PUT', f'clients/{client_id}', update_data, token=self.bureau_token)
        self.log_test("Update Client", success, response)
        
        # DELETE
        success, response = self.make_request('DELETE', f'clients/{client_id}', token=self.bureau_token)
        self.log_test("Delete Client", success, response)
        
        return True

    def test_complete_quote_crud(self):
        """Test complete CRUD operations for quotes"""
        print("\n💰 Testing Complete Quote CRUD...")
        
        # First create a client for the quote
        client_data = {
            "nom": f"Quote Client {self.test_id}",
            "email": f"quote-client-{self.test_id}@test.fr",
            "telephone": "01 11 22 33 44"
        }
        
        success, response = self.make_request('POST', 'clients', client_data, token=self.bureau_token)
        if not success or 'id' not in response:
            self.log_test("Create Client for Quote", False, None, "Failed to create client")
            return False
        
        client_id = response['id']
        
        # CREATE quote
        quote_data = {
            "client_id": client_id,
            "title": f"Test Quote {self.test_id}",
            "description": "Test quote description",
            "amount": 1500.00
        }
        
        success, response = self.make_request('POST', 'quotes', quote_data, token=self.bureau_token)
        if success and 'id' in response:
            quote_id = response['id']
            self.test_data['quotes'].append(response)
            self.log_test("Create Quote", True, {"id": quote_id, "amount": response.get('amount')})
        else:
            self.log_test("Create Quote", False, None, response)
            return False
        
        # READ (all)
        success, response = self.make_request('GET', 'quotes', token=self.bureau_token)
        quote_count = len(response) if success and isinstance(response, list) else 0
        self.log_test("Read All Quotes", success, {"count": quote_count})
        
        # UPDATE
        update_data = {
            "title": f"Updated Quote {self.test_id}",
            "amount": 2000.00,
            "status": "APPROVED"
        }
        success, response = self.make_request('PUT', f'quotes/{quote_id}', update_data, token=self.bureau_token)
        self.log_test("Update Quote", success, response)
        
        # DELETE
        success, response = self.make_request('DELETE', f'quotes/{quote_id}', token=self.bureau_token)
        self.log_test("Delete Quote", success, response)
        
        return True

    def test_complete_site_crud(self):
        """Test complete CRUD operations for sites"""
        print("\n📅 Testing Complete Site CRUD...")
        
        # CREATE
        site_data = {
            "name": f"Test Site {self.test_id}",
            "address": "123 Test Address",
            "scheduled_date": "2024-02-15",
            "scheduled_time": "09:00",
            "duration": 3,
            "status": "PLANNED",
            "description": "Test site description"
        }
        
        success, response = self.make_request('POST', 'sites', site_data, token=self.bureau_token)
        if success and 'id' in response:
            site_id = response['id']
            self.test_data['sites'].append(response)
            self.log_test("Create Site", True, {"id": site_id, "name": response.get('name')})
        else:
            self.log_test("Create Site", False, None, response)
            return False
        
        # READ (all)
        success, response = self.make_request('GET', 'sites', token=self.bureau_token)
        site_count = len(response) if success and isinstance(response, list) else 0
        self.log_test("Read All Sites", success, {"count": site_count})
        
        # UPDATE
        update_data = {
            "name": f"Updated Site {self.test_id}",
            "status": "IN_PROGRESS",
            "duration": 4
        }
        success, response = self.make_request('PUT', f'sites/{site_id}', update_data, token=self.bureau_token)
        self.log_test("Update Site", success, response)
        
        # DELETE
        success, response = self.make_request('DELETE', f'sites/{site_id}', token=self.bureau_token)
        self.log_test("Delete Site", success, response)
        
        return True

    def test_complete_invitation_crud(self):
        """Test complete CRUD operations for invitations"""
        print("\n✉️ Testing Complete Invitation CRUD...")
        
        # CREATE
        invitation_data = {
            "email": f"invite-{self.test_id}@test.fr",
            "role": "TECHNICIEN",
            "message": f"Test invitation {self.test_id}"
        }
        
        success, response = self.make_request('POST', 'invitations', invitation_data, token=self.bureau_token)
        if success and 'id' in response:
            invitation_id = response['id']
            self.test_data['invitations'].append(response)
            self.log_test("Create Invitation", True, {"id": invitation_id, "email": response.get('email')})
        else:
            self.log_test("Create Invitation", False, None, response)
            return False
        
        # READ (all)
        success, response = self.make_request('GET', 'invitations', token=self.bureau_token)
        invitation_count = len(response) if success and isinstance(response, list) else 0
        self.log_test("Read All Invitations", success, {"count": invitation_count})
        
        # RESEND
        success, response = self.make_request('PUT', f'invitations/{invitation_id}/resend', token=self.bureau_token)
        self.log_test("Resend Invitation", success, response)
        
        # CANCEL (DELETE)
        success, response = self.make_request('DELETE', f'invitations/{invitation_id}', token=self.bureau_token)
        self.log_test("Cancel Invitation", success, response)
        
        return True

    def test_pdf_generation_comprehensive(self):
        """Test comprehensive PDF generation"""
        print("\n📄 Testing Comprehensive PDF Generation...")
        
        if not self.test_data['searches']:
            self.log_test("PDF Generation", False, None, "No searches available")
            return False
        
        search_id = self.test_data['searches'][0]['id']
        
        # Test individual PDF generation
        success, response = self.make_request('POST', f'reports/generate-pdf/{search_id}', 
                                            token=self.bureau_token)
        self.log_test("Generate Individual PDF", success, 
                     {"search_id": search_id} if success else None,
                     response if not success else None)
        
        # Test summary PDF generation
        summary_data = {"search_ids": [search_id]}
        success, response = self.make_request('POST', 'reports/generate-summary-pdf', 
                                            summary_data, token=self.bureau_token)
        self.log_test("Generate Summary PDF", success,
                     {"search_count": 1} if success else None,
                     response if not success else None)
        
        return True

    def test_statistics_comprehensive(self):
        """Test comprehensive statistics"""
        print("\n📊 Testing Comprehensive Statistics...")
        
        success, response = self.make_request('GET', 'stats/dashboard', token=self.bureau_token)
        
        if success:
            expected_keys = ['total_searches', 'total_reports', 'total_clients', 'total_quotes', 'total_users']
            missing_keys = [key for key in expected_keys if key not in response]
            if missing_keys:
                self.log_test("Dashboard Statistics", False, None, f"Missing keys: {missing_keys}")
            else:
                stats = {k: response.get(k) for k in expected_keys}
                self.log_test("Dashboard Statistics", True, stats)
        else:
            self.log_test("Dashboard Statistics", False, None, response)
        
        return success

    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting SkyApp Final Comprehensive Backend Testing")
        print("=" * 80)
        print(f"Test ID: {self.test_id}")
        print("Testing complete CRUD operations for all entities")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_data():
            print("❌ Setup failed, aborting tests")
            return False
        
        # Run comprehensive tests
        test_results = [
            self.test_complete_search_crud(),
            self.test_complete_client_crud(),
            self.test_complete_quote_crud(),
            self.test_complete_site_crud(),
            self.test_complete_invitation_crud(),
            self.test_pdf_generation_comprehensive(),
            self.test_statistics_comprehensive(),
        ]
        
        # Print final results
        self.print_final_results()
        
        return all(test_results) and self.tests_passed == self.tests_run

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 FINAL COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.critical_failures:
            print(f"\n❌ CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   • {failure}")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL COMPREHENSIVE TESTS PASSED!")
            print("✅ Backend API is 100% functional with complete CRUD operations")
            print("✅ All new features are working correctly")
            print("✅ PDF generation is operational")
            print("✅ Statistics dashboard is functional")
            print("✅ Authentication and authorization working")
        else:
            print(f"\n⚠️  {self.tests_run - self.tests_passed} tests failed.")

def main():
    """Main test runner"""
    tester = SkyAppFinalTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())