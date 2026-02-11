import requests
import sys
from datetime import datetime
import json

class SearchAppAPITester:
    def __init__(self, base_url="https://smart-inventory-97.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.bureau_token = None
        self.tech_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.bureau_user = None
        self.tech_user = None
        self.search_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, description=""):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        if description:
            print(f"   Description: {description}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 300:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list) and len(response_data) > 0:
                        print(f"   Response: List with {len(response_data)} items")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200,
            description="Check if SearchApp API is running"
        )

    def test_init_sample_data(self):
        """Initialize sample data"""
        success, response = self.run_test(
            "Initialize Sample Data",
            "POST",
            "init-sample-data",
            200,
            description="Create sample company, users, and searches"
        )
        return success

    def test_bureau_login(self):
        """Test Bureau user login"""
        success, response = self.run_test(
            "Bureau Login",
            "POST",
            "auth/login",
            200,
            data={"email": "bureau@search-app.fr", "password": "bureau123"},
            description="Login with Bureau account"
        )
        if success and 'access_token' in response:
            self.bureau_token = response['access_token']
            self.bureau_user = response['user']
            print(f"   Bureau user: {self.bureau_user['prenom']} {self.bureau_user['nom']} ({self.bureau_user['role']})")
            return True
        return False

    def test_tech_login(self):
        """Test Technicien user login"""
        success, response = self.run_test(
            "Technicien Login",
            "POST",
            "auth/login",
            200,
            data={"email": "tech@search-app.fr", "password": "tech123"},
            description="Login with Technicien account"
        )
        if success and 'access_token' in response:
            self.tech_token = response['access_token']
            self.tech_user = response['user']
            print(f"   Tech user: {self.tech_user['prenom']} {self.tech_user['nom']} ({self.tech_user['role']})")
            return True
        return False

    def test_invalid_login(self):
        """Test invalid login credentials"""
        return self.run_test(
            "Invalid Login",
            "POST",
            "auth/login",
            401,
            data={"email": "invalid@test.com", "password": "wrongpass"},
            description="Should fail with invalid credentials"
        )

    def test_auth_me_bureau(self):
        """Test /auth/me endpoint with Bureau token"""
        return self.run_test(
            "Auth Me - Bureau",
            "GET",
            "auth/me",
            200,
            token=self.bureau_token,
            description="Get current user info for Bureau"
        )

    def test_auth_me_tech(self):
        """Test /auth/me endpoint with Tech token"""
        return self.run_test(
            "Auth Me - Tech",
            "GET",
            "auth/me",
            200,
            token=self.tech_token,
            description="Get current user info for Technicien"
        )

    def test_create_search_tech(self):
        """Test creating a search as Technicien"""
        search_data = {
            "location": "Test Location - Chantier API Test",
            "description": "Test search created via API testing",
            "observations": "This is a test observation from API test",
            "latitude": 48.8566,
            "longitude": 2.3522
        }
        success, response = self.run_test(
            "Create Search - Tech",
            "POST",
            "searches",
            200,
            data=search_data,
            token=self.tech_token,
            description="Technicien should be able to create searches"
        )
        if success and 'id' in response:
            self.search_id = response['id']
            print(f"   Created search ID: {self.search_id}")
        return success

    def test_get_searches_tech(self):
        """Test getting searches as Technicien"""
        success, response = self.run_test(
            "Get Searches - Tech",
            "GET",
            "searches",
            200,
            token=self.tech_token,
            description="Technicien should get their searches"
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} searches")
        return success

    def test_get_search_by_id_tech(self):
        """Test getting specific search by ID"""
        if not self.search_id:
            print("   ⚠️  No search ID available, skipping test")
            return True
            
        return self.run_test(
            "Get Search by ID - Tech",
            "GET",
            f"searches/{self.search_id}",
            200,
            token=self.tech_token,
            description="Get specific search by ID"
        )

    def test_update_search_status(self):
        """Test updating search status"""
        if not self.search_id:
            print("   ⚠️  No search ID available, skipping test")
            return True
            
        return self.run_test(
            "Update Search Status",
            "PUT",
            f"searches/{self.search_id}/status",
            200,
            data="SHARED",
            token=self.tech_token,
            description="Update search status to SHARED"
        )

    def test_create_report_bureau(self):
        """Test creating a report as Bureau"""
        if not self.search_id:
            print("   ⚠️  No search ID available, skipping test")
            return True
            
        report_data = {
            "search_id": self.search_id,
            "title": "Test Report",
            "content": "This is a test report created via API testing"
        }
        return self.run_test(
            "Create Report - Bureau",
            "POST",
            "reports",
            200,
            data=report_data,
            token=self.bureau_token,
            description="Bureau should be able to create reports"
        )

    def test_get_reports_bureau(self):
        """Test getting reports as Bureau"""
        return self.run_test(
            "Get Reports - Bureau",
            "GET",
            "reports",
            200,
            token=self.bureau_token,
            description="Bureau should get all reports"
        )

    def test_create_client_bureau(self):
        """Test creating a client as Bureau"""
        client_data = {
            "nom": "Test Client SARL",
            "email": "test-client@example.com",
            "telephone": "01 23 45 67 89",
            "adresse": "123 Test Street, 75001 Paris"
        }
        return self.run_test(
            "Create Client - Bureau",
            "POST",
            "clients",
            200,
            data=client_data,
            token=self.bureau_token,
            description="Bureau should be able to create clients"
        )

    def test_get_clients_bureau(self):
        """Test getting clients as Bureau"""
        return self.run_test(
            "Get Clients - Bureau",
            "GET",
            "clients",
            200,
            token=self.bureau_token,
            description="Bureau should get all clients"
        )

    def test_dashboard_stats(self):
        """Test dashboard stats endpoint"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "stats/dashboard",
            200,
            token=self.bureau_token,
            description="Get dashboard statistics"
        )
        if success:
            expected_keys = ['total_searches', 'total_reports', 'total_clients', 'total_quotes', 'total_users']
            for key in expected_keys:
                if key not in response:
                    print(f"   ⚠️  Missing key in response: {key}")
                    return False
            print(f"   Stats: Searches={response.get('total_searches')}, Reports={response.get('total_reports')}, Clients={response.get('total_clients')}")
        return success

    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        return self.run_test(
            "Unauthorized Access",
            "GET",
            "searches",
            401,
            description="Should fail without authentication token"
        )

    def test_register_new_user(self):
        """Test user registration"""
        timestamp = datetime.now().strftime("%H%M%S")
        register_data = {
            "company_name": f"Test Company {timestamp}",
            "email": f"test{timestamp}@example.com",
            "nom": "Test",
            "prenom": "User",
            "password": "testpass123"
        }
        return self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=register_data,
            description="Register new user and company"
        )

def main():
    print("🚀 Starting SearchApp API Testing...")
    print("=" * 60)
    
    tester = SearchAppAPITester()
    
    # Test sequence
    tests = [
        # Basic connectivity
        ("Root API", tester.test_root_endpoint),
        
        # Data initialization
        ("Sample Data Init", tester.test_init_sample_data),
        
        # Authentication tests
        ("Bureau Login", tester.test_bureau_login),
        ("Tech Login", tester.test_tech_login),
        ("Invalid Login", tester.test_invalid_login),
        ("Unauthorized Access", tester.test_unauthorized_access),
        ("User Registration", tester.test_register_new_user),
        
        # Auth verification
        ("Auth Me Bureau", tester.test_auth_me_bureau),
        ("Auth Me Tech", tester.test_auth_me_tech),
        
        # Search operations
        ("Create Search Tech", tester.test_create_search_tech),
        ("Get Searches Tech", tester.test_get_searches_tech),
        ("Get Search by ID", tester.test_get_search_by_id_tech),
        ("Update Search Status", tester.test_update_search_status),
        
        # Report operations
        ("Create Report Bureau", tester.test_create_report_bureau),
        ("Get Reports Bureau", tester.test_get_reports_bureau),
        
        # Client operations
        ("Create Client Bureau", tester.test_create_client_bureau),
        ("Get Clients Bureau", tester.test_get_clients_bureau),
        
        # Dashboard stats
        ("Dashboard Stats", tester.test_dashboard_stats),
    ]
    
    # Run all tests
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            tester.tests_run += 1
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())