#!/usr/bin/env python3
"""
SkyApp Backend Regression Testing - Post Frontend Layout Modification
Testing core backend functionality after frontend layout changes to ensure no regressions.

Focus Areas:
1. Core Backend Health Check - verify all API endpoints are functioning
2. Authentication System - test login/register endpoints  
3. Basic CRUD Operations - test core endpoints like /api/searches, /api/users
4. User Stats Endpoint - test /api/stats/users used by About section
5. No Regression Testing - ensure layout change didn't break backend functionality

Test Credentials:
- tech@search-app.fr / tech123 
- bureau@search-app.fr / bureau123
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Use environment variable from frontend/.env
BACKEND_URL = "https://smart-inventory-97.preview.emergentagent.com/api"

class LayoutRegressionTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.user_data = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
    
    def test_backend_health(self):
        """Test basic backend health and connectivity"""
        print("\n🏥 BACKEND HEALTH CHECK")
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Root Endpoint", True, f"Response: {data.get('message', 'OK')}")
            else:
                self.log_test("Backend Root Endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Backend Root Endpoint", False, f"Connection error: {str(e)}")
    
    def test_authentication_system(self):
        """Test authentication endpoints with provided credentials"""
        print("\n🔐 AUTHENTICATION SYSTEM TESTING")
        
        # Initialize sample data first
        try:
            response = requests.post(f"{self.base_url}/init-sample-data", timeout=10)
            self.log_test("Sample Data Initialization", response.status_code in [200, 201], 
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Sample Data Initialization", False, f"Error: {str(e)}")
        
        # Test login with tech credentials
        try:
            login_data = {
                "email": "tech@search-app.fr",
                "password": "tech123"
            }
            response = requests.post(f"{self.base_url}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.user_data = data.get('user')
                self.log_test("Tech User Login", True, f"Token received, User: {self.user_data.get('email')}")
            else:
                self.log_test("Tech User Login", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Tech User Login", False, f"Error: {str(e)}")
        
        # Test login with bureau credentials
        try:
            login_data = {
                "email": "bureau@search-app.fr", 
                "password": "bureau123"
            }
            response = requests.post(f"{self.base_url}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Bureau User Login", True, f"User: {data.get('user', {}).get('email')}")
            else:
                self.log_test("Bureau User Login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Bureau User Login", False, f"Error: {str(e)}")
        
        # Test /auth/me endpoint
        if self.token:
            try:
                headers = {"Authorization": f"Bearer {self.token}"}
                response = requests.get(f"{self.base_url}/auth/me", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Auth Me Endpoint", True, f"User ID: {data.get('id', 'N/A')}")
                else:
                    self.log_test("Auth Me Endpoint", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Auth Me Endpoint", False, f"Error: {str(e)}")
    
    def test_basic_crud_operations(self):
        """Test basic CRUD operations on core endpoints"""
        print("\n📝 BASIC CRUD OPERATIONS TESTING")
        
        if not self.token:
            self.log_test("CRUD Operations", False, "No authentication token available")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test GET /api/searches
        try:
            response = requests.get(f"{self.base_url}/searches", headers=headers, timeout=10)
            if response.status_code == 200:
                searches = response.json()
                self.log_test("GET /api/searches", True, f"Retrieved {len(searches)} searches")
            else:
                self.log_test("GET /api/searches", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/searches", False, f"Error: {str(e)}")
        
        # Test GET /api/clients
        try:
            response = requests.get(f"{self.base_url}/clients", headers=headers, timeout=10)
            if response.status_code == 200:
                clients = response.json()
                self.log_test("GET /api/clients", True, f"Retrieved {len(clients)} clients")
            else:
                self.log_test("GET /api/clients", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/clients", False, f"Error: {str(e)}")
        
        # Test GET /api/quotes
        try:
            response = requests.get(f"{self.base_url}/quotes", headers=headers, timeout=10)
            if response.status_code == 200:
                quotes = response.json()
                self.log_test("GET /api/quotes", True, f"Retrieved {len(quotes)} quotes")
            else:
                self.log_test("GET /api/quotes", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/quotes", False, f"Error: {str(e)}")
        
        # Test GET /api/reports
        try:
            response = requests.get(f"{self.base_url}/reports", headers=headers, timeout=10)
            if response.status_code == 200:
                reports = response.json()
                self.log_test("GET /api/reports", True, f"Retrieved {len(reports)} reports")
            else:
                self.log_test("GET /api/reports", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/reports", False, f"Error: {str(e)}")
    
    def test_user_stats_endpoint(self):
        """Test the /api/stats/dashboard endpoint used by About section"""
        print("\n📊 USER STATS ENDPOINT TESTING")
        
        if not self.token:
            self.log_test("Stats Dashboard", False, "No authentication token available")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.base_url}/stats/dashboard", headers=headers, timeout=10)
            if response.status_code == 200:
                stats = response.json()
                required_fields = ['total_searches', 'total_reports', 'total_clients', 'total_quotes', 'total_users']
                
                missing_fields = [field for field in required_fields if field not in stats]
                if not missing_fields:
                    self.log_test("Stats Dashboard Endpoint", True, 
                                f"All required fields present. Users: {stats.get('total_users', 0)}")
                else:
                    self.log_test("Stats Dashboard Endpoint", False, 
                                f"Missing fields: {missing_fields}")
            else:
                self.log_test("Stats Dashboard Endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Stats Dashboard Endpoint", False, f"Error: {str(e)}")
    
    def test_pdf_generation_endpoints(self):
        """Test PDF generation endpoints to ensure they're still functional"""
        print("\n📄 PDF GENERATION ENDPOINTS TESTING")
        
        if not self.token:
            self.log_test("PDF Generation", False, "No authentication token available")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # First get a search to test PDF generation
        try:
            response = requests.get(f"{self.base_url}/searches", headers=headers, timeout=10)
            if response.status_code == 200:
                searches = response.json()
                if searches:
                    search_id = searches[0]['id']
                    
                    # Test individual PDF generation
                    try:
                        response = requests.post(f"{self.base_url}/reports/generate-pdf/{search_id}", 
                                               headers=headers, timeout=15)
                        if response.status_code == 200:
                            self.log_test("Individual PDF Generation", True, 
                                        f"PDF generated for search {search_id[:8]}")
                        else:
                            self.log_test("Individual PDF Generation", False, 
                                        f"Status: {response.status_code}")
                    except Exception as e:
                        self.log_test("Individual PDF Generation", False, f"Error: {str(e)}")
                    
                    # Test summary PDF generation
                    try:
                        pdf_data = {"search_ids": [search_id]}
                        response = requests.post(f"{self.base_url}/reports/generate-summary-pdf", 
                                               json=pdf_data, headers=headers, timeout=15)
                        if response.status_code == 200:
                            self.log_test("Summary PDF Generation", True, "Summary PDF generated successfully")
                        else:
                            self.log_test("Summary PDF Generation", False, f"Status: {response.status_code}")
                    except Exception as e:
                        self.log_test("Summary PDF Generation", False, f"Error: {str(e)}")
                else:
                    self.log_test("PDF Generation", False, "No searches available for PDF testing")
            else:
                self.log_test("PDF Generation", False, "Could not retrieve searches for PDF testing")
        except Exception as e:
            self.log_test("PDF Generation", False, f"Error retrieving searches: {str(e)}")
    
    def test_enhanced_endpoints(self):
        """Test enhanced endpoints that might be affected by layout changes"""
        print("\n🚀 ENHANCED ENDPOINTS TESTING")
        
        if not self.token:
            self.log_test("Enhanced Endpoints", False, "No authentication token available")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test team leaders endpoint
        try:
            response = requests.get(f"{self.base_url}/team-leaders", headers=headers, timeout=10)
            if response.status_code == 200:
                team_leaders = response.json()
                self.log_test("GET /api/team-leaders", True, f"Retrieved {len(team_leaders)} team leaders")
            else:
                self.log_test("GET /api/team-leaders", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/team-leaders", False, f"Error: {str(e)}")
        
        # Test collaborators endpoint
        try:
            response = requests.get(f"{self.base_url}/collaborators", headers=headers, timeout=10)
            if response.status_code == 200:
                collaborators = response.json()
                self.log_test("GET /api/collaborators", True, f"Retrieved {len(collaborators)} collaborators")
            else:
                self.log_test("GET /api/collaborators", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/collaborators", False, f"Error: {str(e)}")
        
        # Test schedules endpoint
        try:
            response = requests.get(f"{self.base_url}/schedules", headers=headers, timeout=10)
            if response.status_code == 200:
                schedules = response.json()
                self.log_test("GET /api/schedules", True, f"Retrieved {len(schedules)} schedules")
            else:
                self.log_test("GET /api/schedules", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/schedules", False, f"Error: {str(e)}")
        
        # Test worksites endpoint
        try:
            response = requests.get(f"{self.base_url}/worksites", headers=headers, timeout=10)
            if response.status_code == 200:
                worksites = response.json()
                self.log_test("GET /api/worksites", True, f"Retrieved {len(worksites)} worksites")
            else:
                self.log_test("GET /api/worksites", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/worksites", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all regression tests"""
        print("🧪 SKYAPP BACKEND REGRESSION TESTING - POST FRONTEND LAYOUT MODIFICATION")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Run all test suites
        self.test_backend_health()
        self.test_authentication_system()
        self.test_basic_crud_operations()
        self.test_user_stats_endpoint()
        self.test_pdf_generation_endpoints()
        self.test_enhanced_endpoints()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📋 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 REGRESSION ANALYSIS:")
        if success_rate >= 95:
            print("✅ EXCELLENT - No significant regressions detected. Frontend layout changes did not impact backend functionality.")
        elif success_rate >= 85:
            print("⚠️  GOOD - Minor issues detected but core functionality intact. Layout changes appear safe.")
        elif success_rate >= 70:
            print("⚠️  MODERATE - Some functionality affected. Review failed tests for potential regressions.")
        else:
            print("❌ CRITICAL - Significant backend issues detected. Layout changes may have caused regressions.")
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = LayoutRegressionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)