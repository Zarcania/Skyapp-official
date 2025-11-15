#!/usr/bin/env python3
"""
Clean Backend Test for SkyApp - Avoids data conflicts
Tests all new functionalities with unique data each run
"""

import requests
import sys
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class SkyAppCleanTester:
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
        self.company_id = None
        
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
        self.unique_email = f"test-{self.test_id}@btp-test.fr"
        self.unique_company = f"BTP Test {self.test_id}"

    def log_test(self, name: str, success: bool, response_data: Any = None, error: str = None):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if response_data and isinstance(response_data, dict) and len(str(response_data)) < 300:
                print(f"   Response: {response_data}")
        else:
            print(f"❌ {name}")
            if error:
                print(f"   Error: {error}")
            self.critical_failures.append(f"{name}: {error}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    token: str = None, files: Dict = None, 
                    expected_status: int = 200, raw_data: str = None) -> tuple[bool, Any]:
        """Make HTTP request and return success status and response data"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files, 
                                           headers={k: v for k, v in headers.items() if k != 'Content-Type'}, 
                                           timeout=15)
                else:
                    headers['Content-Type'] = 'application/json'
                    response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                if raw_data is not None:
                    headers['Content-Type'] = 'text/plain'
                    response = requests.put(url, data=raw_data, headers=headers, timeout=15)
                elif files:
                    response = requests.put(url, data=data, files=files,
                                          headers={k: v for k, v in headers.items() if k != 'Content-Type'},
                                          timeout=15)
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

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.make_request('GET', '')
        self.log_test("Root API Endpoint", success, response)
        return success

    def test_register_new_company(self):
        """Test company registration with unique data"""
        register_data = {
            "company_name": self.unique_company,
            "email": self.unique_email,
            "nom": "Dubois",
            "prenom": "Marie",
            "password": "admin123secure"
        }
        
        success, response = self.make_request('POST', 'auth/register', register_data)
        
        if success and 'access_token' in response:
            self.bureau_token = response['access_token']
            self.bureau_user = response['user']
            self.company_id = self.bureau_user['company_id']
            
        self.log_test("Company Registration", success, 
                     {"user_role": response.get('user', {}).get('role')} if success else None,
                     response if not success else None)
        return success

    def test_login_bureau(self):
        """Test Bureau user login"""
        login_data = {
            "email": self.unique_email,
            "password": "admin123secure"
        }
        
        success, response = self.make_request('POST', 'auth/login', login_data)
        
        if success and 'access_token' in response:
            self.bureau_token = response['access_token']
            self.bureau_user = response['user']
            
        self.log_test("Bureau Login", success, 
                     {"role": response.get('user', {}).get('role')} if success else None,
                     response if not success else None)
        return success

    def test_auth_me(self):
        """Test /auth/me endpoint"""
        success, response = self.make_request('GET', 'auth/me', token=self.bureau_token)
        self.log_test("Auth Me Endpoint", success, 
                     {"email": response.get('email'), "role": response.get('role')} if success else None,
                     response if not success else None)
        return success

    def test_create_search(self):
        """Test creating a new search"""
        search_data = {
            "location": f"Chantier Test {self.test_id} - Rue de Rivoli, Paris 1er",
            "description": "Recherche de canalisations d'eau potable sous chaussée",
            "observations": "Zone à forte circulation, intervention de nuit recommandée. Sol pavé ancien.",
            "latitude": 48.8606,
            "longitude": 2.3376,
            "photos": ["photo1.jpg", "photo2.jpg"]
        }
        
        success, response = self.make_request('POST', 'searches', search_data, token=self.bureau_token)
        
        if success and 'id' in response:
            self.test_data['searches'].append(response)
            
        self.log_test("Create Search", success, 
                     {"id": response.get('id'), "location": response.get('location')} if success else None,
                     response if not success else None)
        return success

    def test_get_searches(self):
        """Test retrieving searches"""
        success, response = self.make_request('GET', 'searches', token=self.bureau_token)
        
        search_count = len(response) if success and isinstance(response, list) else 0
        self.log_test("Get Searches", success, 
                     {"count": search_count} if success else None,
                     response if not success else None)
        return success

    def test_update_search_status(self):
        """Test updating search status with correct implementation"""
        if not self.test_data['searches']:
            self.log_test("Update Search Status", False, None, "No searches available for testing")
            return False
            
        search_id = self.test_data['searches'][0]['id']
        
        # Use raw_data parameter for text/plain content
        success, response = self.make_request('PUT', f'searches/{search_id}/status', 
                                            token=self.bureau_token, raw_data="SHARED")
        
        self.log_test("Update Search Status", success, response,
                     response if not success else None)
        return success

    def test_create_report(self):
        """Test creating a report"""
        if not self.test_data['searches']:
            self.log_test("Create Report", False, None, "No searches available for report creation")
            return False
            
        report_data = {
            "search_id": self.test_data['searches'][0]['id'],
            "title": f"Rapport d'intervention Test {self.test_id}",
            "content": "Intervention réalisée avec succès. Canalisations localisées à 1,2m de profondeur. État général satisfaisant."
        }
        
        success, response = self.make_request('POST', 'reports', report_data, token=self.bureau_token)
        
        if success and 'id' in response:
            self.test_data['reports'].append(response)
            
        self.log_test("Create Report", success,
                     {"id": response.get('id'), "title": response.get('title')} if success else None,
                     response if not success else None)
        return success

    def test_create_client(self):
        """Test creating a client"""
        client_data = {
            "nom": f"Client Test {self.test_id}",
            "email": f"client-{self.test_id}@test.fr",
            "telephone": "01 42 86 75 30",
            "adresse": "15 Avenue Montaigne, 75008 Paris"
        }
        
        success, response = self.make_request('POST', 'clients', client_data, token=self.bureau_token)
        
        if success and 'id' in response:
            self.test_data['clients'].append(response)
            
        self.log_test("Create Client", success,
                     {"id": response.get('id'), "nom": response.get('nom')} if success else None,
                     response if not success else None)
        return success

    def test_create_quote(self):
        """Test creating a quote"""
        if not self.test_data['clients']:
            self.log_test("Create Quote", False, None, "No clients available for quote creation")
            return False
            
        quote_data = {
            "client_id": self.test_data['clients'][0]['id'],
            "title": f"Devis Test {self.test_id}",
            "description": "Prestation de recherche et localisation de canalisations d'eau potable.",
            "amount": 2850.00
        }
        
        success, response = self.make_request('POST', 'quotes', quote_data, token=self.bureau_token)
        
        if success and 'id' in response:
            self.test_data['quotes'].append(response)
            
        self.log_test("Create Quote", success,
                     {"id": response.get('id'), "amount": response.get('amount')} if success else None,
                     response if not success else None)
        return success

    def test_create_site(self):
        """Test creating a site/planning entry"""
        site_data = {
            "name": f"Intervention Test {self.test_id}",
            "address": "Rue de Rivoli, 75001 Paris",
            "scheduled_date": "2024-01-15",
            "scheduled_time": "08:00",
            "duration": 4,
            "technician_assigned": self.bureau_user['id'],
            "status": "PLANNED",
            "description": "Recherche de canalisations avec équipement de détection",
            "client_contact": "M. Dupont - 01 42 86 75 30"
        }
        
        success, response = self.make_request('POST', 'sites', site_data, token=self.bureau_token)
        
        if success and 'id' in response:
            self.test_data['sites'].append(response)
            
        self.log_test("Create Site/Planning", success,
                     {"id": response.get('id'), "name": response.get('name')} if success else None,
                     response if not success else None)
        return success

    def test_create_invitation(self):
        """Test creating an invitation"""
        invitation_data = {
            "email": f"tech-{self.test_id}@test.fr",
            "role": "TECHNICIEN",
            "message": f"Test invitation {self.test_id}"
        }
        
        success, response = self.make_request('POST', 'invitations', invitation_data, token=self.bureau_token)
        
        if success and 'id' in response:
            self.test_data['invitations'].append(response)
            
        self.log_test("Create Invitation", success,
                     {"id": response.get('id'), "email": response.get('email')} if success else None,
                     response if not success else None)
        return success

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        success, response = self.make_request('GET', 'stats/dashboard', token=self.bureau_token)
        
        if success:
            expected_keys = ['total_searches', 'total_reports', 'total_clients', 'total_quotes', 'total_users']
            missing_keys = [key for key in expected_keys if key not in response]
            if missing_keys:
                success = False
                response = f"Missing keys: {missing_keys}"
        
        self.log_test("Dashboard Statistics", success,
                     {k: response.get(k) for k in ['total_searches', 'total_reports', 'total_clients'] if k in response} if success else None,
                     response if not success else None)
        return success

    def test_generate_search_pdf(self):
        """Test PDF generation for a search"""
        if not self.test_data['searches']:
            self.log_test("Generate Search PDF", False, None, "No searches available for PDF generation")
            return False
            
        search_id = self.test_data['searches'][0]['id']
        
        success, response = self.make_request('POST', f'reports/generate-pdf/{search_id}', 
                                            token=self.bureau_token)
        
        pdf_success = success and response is not None
        
        self.log_test("Generate Search PDF", pdf_success,
                     {"search_id": search_id, "response_type": type(response).__name__} if pdf_success else None,
                     response if not pdf_success else None)
        return pdf_success

    def test_generate_summary_pdf(self):
        """Test PDF generation for multiple searches (summary)"""
        if len(self.test_data['searches']) < 1:
            self.log_test("Generate Summary PDF", False, None, "Need at least 1 search for summary PDF")
            return False
            
        search_ids = [search['id'] for search in self.test_data['searches'][:1]]
        summary_data = {"search_ids": search_ids}
        
        success, response = self.make_request('POST', 'reports/generate-summary-pdf', 
                                            summary_data, token=self.bureau_token)
        
        pdf_success = success and response is not None
        
        self.log_test("Generate Summary PDF", pdf_success,
                     {"search_count": len(search_ids), "response_type": type(response).__name__} if pdf_success else None,
                     response if not pdf_success else None)
        return pdf_success

    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting SkyApp Clean Backend Testing")
        print("=" * 80)
        print(f"Test ID: {self.test_id}")
        print(f"Unique Email: {self.unique_email}")
        print(f"Unique Company: {self.unique_company}")
        print("=" * 80)
        
        # Test sequence
        tests = [
            ("Root API Endpoint", self.test_root_endpoint),
            ("Company Registration", self.test_register_new_company),
            ("Bureau Login", self.test_login_bureau),
            ("Auth Me Endpoint", self.test_auth_me),
            ("Create Search", self.test_create_search),
            ("Get Searches", self.test_get_searches),
            ("Update Search Status", self.test_update_search_status),
            ("Create Report", self.test_create_report),
            ("Create Client", self.test_create_client),
            ("Create Quote", self.test_create_quote),
            ("Create Site/Planning", self.test_create_site),
            ("Create Invitation", self.test_create_invitation),
            ("Dashboard Statistics", self.test_dashboard_stats),
            ("Generate Search PDF", self.test_generate_search_pdf),
            ("Generate Summary PDF", self.test_generate_summary_pdf),
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_test(test_name, False, None, f"Exception: {str(e)}")
        
        # Print final results
        self.print_final_results()
        
        return self.tests_passed == self.tests_run

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 CLEAN TEST RESULTS")
        print("=" * 80)
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.critical_failures:
            print(f"\n❌ CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   • {failure}")
        
        print(f"\n📈 DATA CREATED DURING TESTING:")
        for data_type, items in self.test_data.items():
            print(f"   • {data_type.title()}: {len(items)} items")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL TESTS PASSED! Backend is 100% functional.")
        else:
            print(f"\n⚠️  {self.tests_run - self.tests_passed} tests failed. Check details above.")

def main():
    """Main test runner"""
    tester = SkyAppCleanTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())