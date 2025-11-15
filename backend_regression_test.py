#!/usr/bin/env python3
"""
SkyApp Backend Regression Testing
Comprehensive testing after frontend UI fixes to ensure no backend functionality was impacted.

Testing Areas:
1. Authentication System
2. Core CRUD Operations  
3. PDF Generation
4. Statistics Dashboard
5. Search Management
6. Enhanced Features
"""

import requests
import json
import os
import tempfile
from datetime import datetime
from PIL import Image
import io

# Configuration
BACKEND_URL = "https://smart-inventory-97.preview.emergentagent.com/api"

class BackendRegressionTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_data = None
        self.company_id = None
        self.test_results = []
        self.created_resources = {
            'searches': [],
            'clients': [],
            'quotes': [],
            'reports': [],
            'team_leaders': [],
            'collaborators': [],
            'schedules': [],
            'worksites': []
        }
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def setup_sample_data(self):
        """Initialize sample data"""
        try:
            response = self.session.post(f"{BACKEND_URL}/init-sample-data", timeout=10)
            if response.status_code == 200:
                self.log_result("Sample Data Setup", True, "Sample data initialized")
                return True
            else:
                self.log_result("Sample Data Setup", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Sample Data Setup", False, f"Error: {str(e)}")
            return False
    
    def test_authentication_system(self):
        """Test 1: Authentication System - Login/logout, JWT token validation"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        
        # Test 1.1: Login with Technicien credentials
        try:
            login_data = {"email": "tech@search-app.fr", "password": "tech123"}
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.user_data = data["user"]
                self.company_id = self.user_data["company_id"]
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                self.log_result("Technicien Login", True, f"Logged in as {data['user']['email']}")
            else:
                self.log_result("Technicien Login", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Technicien Login", False, f"Error: {str(e)}")
            return False
        
        # Test 1.2: JWT Token Validation via /auth/me
        try:
            response = self.session.get(f"{BACKEND_URL}/auth/me", timeout=10)
            if response.status_code == 200:
                user_info = response.json()
                if user_info.get('email') == 'tech@search-app.fr':
                    self.log_result("JWT Token Validation", True, f"Token valid for user: {user_info['email']}")
                else:
                    self.log_result("JWT Token Validation", False, "Token validation returned wrong user")
            else:
                self.log_result("JWT Token Validation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("JWT Token Validation", False, f"Error: {str(e)}")
        
        # Test 1.3: Login with Bureau credentials
        try:
            login_data = {"email": "bureau@search-app.fr", "password": "bureau123"}
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                bureau_token = data["access_token"]
                self.log_result("Bureau Login", True, f"Bureau user login successful: {data['user']['email']}")
                # Switch back to technicien for remaining tests
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            else:
                self.log_result("Bureau Login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Bureau Login", False, f"Error: {str(e)}")
        
        return True
    
    def test_core_crud_operations(self):
        """Test 2: Core CRUD Operations - Searches, Reports, Clients, Quotes"""
        print("\n📋 TESTING CORE CRUD OPERATIONS")
        
        # Test 2.1: Search CRUD
        try:
            # Create search (using FormData format as required by the API)
            search_data = {
                "location": "Test Site - Regression Testing",
                "description": "Backend regression test search",
                "observations": "Testing CRUD operations after frontend fixes",
                "latitude": 48.8566,
                "longitude": 2.3522
            }
            
            response = self.session.post(f"{BACKEND_URL}/searches", data=search_data, timeout=10)
            if response.status_code == 200:
                search = response.json()
                search_id = search.get('id')
                self.created_resources['searches'].append(search_id)
                self.log_result("Search Creation", True, f"Search created with ID: {search_id}")
                
                # Read search
                response = self.session.get(f"{BACKEND_URL}/searches/{search_id}", timeout=10)
                if response.status_code == 200:
                    self.log_result("Search Read", True, "Search retrieved successfully")
                else:
                    self.log_result("Search Read", False, f"Status: {response.status_code}")
                
                # Update search
                update_data = {
                    "location": "Updated Test Site",
                    "description": "Updated description for regression test",
                    "observations": "Updated observations"
                }
                response = self.session.put(f"{BACKEND_URL}/searches/{search_id}", json=update_data, timeout=10)
                if response.status_code == 200:
                    self.log_result("Search Update", True, "Search updated successfully")
                else:
                    self.log_result("Search Update", False, f"Status: {response.status_code}")
            else:
                self.log_result("Search Creation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Search CRUD", False, f"Error: {str(e)}")
        
        # Test 2.2: Client CRUD
        try:
            # Create client
            client_data = {
                "nom": "Test Client Regression",
                "email": "test.client@regression.com",
                "telephone": "01 23 45 67 89",
                "adresse": "123 Test Street, Regression City"
            }
            
            response = self.session.post(f"{BACKEND_URL}/clients", json=client_data, timeout=10)
            if response.status_code == 200:
                client = response.json()
                client_id = client.get('id')
                self.created_resources['clients'].append(client_id)
                self.log_result("Client Creation", True, f"Client created: {client['nom']}")
                
                # Read clients
                response = self.session.get(f"{BACKEND_URL}/clients", timeout=10)
                if response.status_code == 200:
                    clients = response.json()
                    self.log_result("Client Read", True, f"Retrieved {len(clients)} clients")
                else:
                    self.log_result("Client Read", False, f"Status: {response.status_code}")
            else:
                self.log_result("Client Creation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Client CRUD", False, f"Error: {str(e)}")
        
        # Test 2.3: Quote CRUD
        try:
            if self.created_resources['clients']:
                client_id = self.created_resources['clients'][0]
                quote_data = {
                    "client_id": client_id,
                    "title": "Test Quote Regression",
                    "description": "Regression testing quote",
                    "amount": 1500.00
                }
                
                response = self.session.post(f"{BACKEND_URL}/quotes", json=quote_data, timeout=10)
                if response.status_code == 200:
                    quote = response.json()
                    quote_id = quote.get('id')
                    self.created_resources['quotes'].append(quote_id)
                    self.log_result("Quote Creation", True, f"Quote created: {quote['title']}")
                    
                    # Read quotes
                    response = self.session.get(f"{BACKEND_URL}/quotes", timeout=10)
                    if response.status_code == 200:
                        quotes = response.json()
                        self.log_result("Quote Read", True, f"Retrieved {len(quotes)} quotes")
                    else:
                        self.log_result("Quote Read", False, f"Status: {response.status_code}")
                else:
                    self.log_result("Quote Creation", False, f"Status: {response.status_code}")
            else:
                self.log_result("Quote Creation", False, "No client available for quote creation")
        except Exception as e:
            self.log_result("Quote CRUD", False, f"Error: {str(e)}")
        
        # Test 2.4: Report CRUD
        try:
            if self.created_resources['searches']:
                search_id = self.created_resources['searches'][0]
                report_data = {
                    "search_id": search_id,
                    "title": "Test Report Regression",
                    "content": "Regression testing report content"
                }
                
                response = self.session.post(f"{BACKEND_URL}/reports", json=report_data, timeout=10)
                if response.status_code == 200:
                    report = response.json()
                    report_id = report.get('id')
                    self.created_resources['reports'].append(report_id)
                    self.log_result("Report Creation", True, f"Report created: {report['title']}")
                    
                    # Read reports
                    response = self.session.get(f"{BACKEND_URL}/reports", timeout=10)
                    if response.status_code == 200:
                        reports = response.json()
                        self.log_result("Report Read", True, f"Retrieved {len(reports)} reports")
                    else:
                        self.log_result("Report Read", False, f"Status: {response.status_code}")
                else:
                    self.log_result("Report Creation", False, f"Status: {response.status_code}")
            else:
                self.log_result("Report Creation", False, "No search available for report creation")
        except Exception as e:
            self.log_result("Report CRUD", False, f"Error: {str(e)}")
    
    def test_pdf_generation(self):
        """Test 3: PDF Generation - Individual and Summary PDFs"""
        print("\n📄 TESTING PDF GENERATION")
        
        # Test 3.1: Individual PDF Generation
        try:
            if self.created_resources['searches']:
                search_id = self.created_resources['searches'][0]
                response = self.session.post(f"{BACKEND_URL}/reports/generate-pdf/{search_id}", timeout=30)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    content_length = len(response.content)
                    if 'application/pdf' in content_type and content_length > 1000:
                        self.log_result("Individual PDF Generation", True, f"PDF generated: {content_length} bytes")
                    else:
                        self.log_result("Individual PDF Generation", False, f"Invalid PDF: {content_type}, {content_length} bytes")
                else:
                    self.log_result("Individual PDF Generation", False, f"Status: {response.status_code}")
            else:
                self.log_result("Individual PDF Generation", False, "No search available for PDF generation")
        except Exception as e:
            self.log_result("Individual PDF Generation", False, f"Error: {str(e)}")
        
        # Test 3.2: Summary PDF Generation
        try:
            if self.created_resources['searches']:
                search_ids = self.created_resources['searches'][:2]  # Use first 2 searches
                pdf_data = {"search_ids": search_ids}
                
                response = self.session.post(f"{BACKEND_URL}/reports/generate-summary-pdf", 
                                           json=pdf_data, timeout=30)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    content_length = len(response.content)
                    if 'application/pdf' in content_type and content_length > 1000:
                        self.log_result("Summary PDF Generation", True, f"Summary PDF generated: {content_length} bytes")
                    else:
                        self.log_result("Summary PDF Generation", False, f"Invalid PDF: {content_type}, {content_length} bytes")
                else:
                    self.log_result("Summary PDF Generation", False, f"Status: {response.status_code}")
            else:
                self.log_result("Summary PDF Generation", False, "No searches available for summary PDF")
        except Exception as e:
            self.log_result("Summary PDF Generation", False, f"Error: {str(e)}")
    
    def test_statistics_dashboard(self):
        """Test 4: Statistics Dashboard - /api/stats/dashboard endpoint"""
        print("\n📊 TESTING STATISTICS DASHBOARD")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/stats/dashboard", timeout=10)
            
            if response.status_code == 200:
                stats = response.json()
                required_fields = ['total_searches', 'total_reports', 'total_clients', 
                                 'total_quotes', 'total_users', 'recent_searches']
                
                missing_fields = [field for field in required_fields if field not in stats]
                
                if not missing_fields:
                    self.log_result("Statistics Dashboard", True, 
                                  f"All required fields present: searches={stats.get('total_searches')}, "
                                  f"reports={stats.get('total_reports')}, clients={stats.get('total_clients')}, "
                                  f"quotes={stats.get('total_quotes')}, users={stats.get('total_users')}")
                else:
                    self.log_result("Statistics Dashboard", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("Statistics Dashboard", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Statistics Dashboard", False, f"Error: {str(e)}")
    
    def test_search_management(self):
        """Test 5: Search Management - Status updates, search sharing"""
        print("\n🔍 TESTING SEARCH MANAGEMENT")
        
        # Test 5.1: Search Status Update
        try:
            if self.created_resources['searches']:
                search_id = self.created_resources['searches'][0]
                
                # Update search status
                response = self.session.put(f"{BACKEND_URL}/searches/{search_id}/status",
                                          data="SHARED", 
                                          headers={"Content-Type": "text/plain"},
                                          timeout=10)
                
                if response.status_code == 200:
                    self.log_result("Search Status Update", True, "Status updated to SHARED")
                else:
                    self.log_result("Search Status Update", False, f"Status: {response.status_code}")
            else:
                self.log_result("Search Status Update", False, "No search available for status update")
        except Exception as e:
            self.log_result("Search Status Update", False, f"Error: {str(e)}")
        
        # Test 5.2: Search Listing
        try:
            response = self.session.get(f"{BACKEND_URL}/searches", timeout=10)
            
            if response.status_code == 200:
                searches = response.json()
                if isinstance(searches, list):
                    self.log_result("Search Listing", True, f"Retrieved {len(searches)} searches")
                else:
                    self.log_result("Search Listing", False, "Invalid response format")
            else:
                self.log_result("Search Listing", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Search Listing", False, f"Error: {str(e)}")
        
        # Test 5.3: Share to Bureau
        try:
            if self.created_resources['searches']:
                search_ids = self.created_resources['searches'][:1]  # Use first search
                share_data = {"search_ids": search_ids}
                
                response = self.session.post(f"{BACKEND_URL}/reports/share-to-bureau",
                                           json=share_data, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_result("Share to Bureau", True, f"Shared {result.get('reports_created', 0)} reports")
                else:
                    self.log_result("Share to Bureau", False, f"Status: {response.status_code}")
            else:
                self.log_result("Share to Bureau", False, "No searches available for sharing")
        except Exception as e:
            self.log_result("Share to Bureau", False, f"Error: {str(e)}")
    
    def test_enhanced_features(self):
        """Test 6: Enhanced Features - FormData, Scheduling, Quote-to-Worksite"""
        print("\n⚡ TESTING ENHANCED FEATURES")
        
        # Test 6.1: FormData with Photo Upload
        try:
            # Create a test image
            img = Image.new('RGB', (400, 300), color='blue')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            # Test FormData submission
            form_data = {
                'location': 'FormData Test Site',
                'description': 'Testing FormData photo upload functionality',
                'observations': 'Regression test for photo upload',
                'latitude': 48.8566,
                'longitude': 2.3522,
                'photo_numbers': [1]
            }
            
            files = [('photos', ('test_photo.jpg', img_buffer, 'image/jpeg'))]
            
            response = self.session.post(f"{BACKEND_URL}/searches",
                                       data=form_data,
                                       files=files,
                                       timeout=20)
            
            if response.status_code == 200:
                search = response.json()
                search_id = search.get('id')
                photos = search.get('photos', [])
                self.created_resources['searches'].append(search_id)
                self.log_result("FormData Photo Upload", True, f"Search created with {len(photos)} photos")
            else:
                self.log_result("FormData Photo Upload", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("FormData Photo Upload", False, f"Error: {str(e)}")
        
        # Test 6.2: Team Leaders Management
        try:
            # Create team leader
            leader_data = {
                "nom": "Test Leader",
                "prenom": "Regression",
                "email": "leader@regression.test",
                "telephone": "01 23 45 67 89",
                "specialite": "Testing",
                "couleur": "#FF5733"
            }
            
            response = self.session.post(f"{BACKEND_URL}/team-leaders", json=leader_data, timeout=10)
            
            if response.status_code == 200:
                leader = response.json()
                leader_id = leader.get('id')
                self.created_resources['team_leaders'].append(leader_id)
                self.log_result("Team Leaders Management", True, f"Team leader created: {leader['prenom']} {leader['nom']}")
            else:
                self.log_result("Team Leaders Management", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Team Leaders Management", False, f"Error: {str(e)}")
        
        # Test 6.3: Quote-to-Worksite Conversion
        try:
            if self.created_resources['quotes']:
                quote_id = self.created_resources['quotes'][0]
                
                # First update quote status to ACCEPTED
                update_data = {"status": "ACCEPTED"}
                response = self.session.put(f"{BACKEND_URL}/quotes/{quote_id}", json=update_data, timeout=10)
                
                if response.status_code == 200:
                    # Now convert to worksite
                    response = self.session.post(f"{BACKEND_URL}/quotes/{quote_id}/convert-to-worksite", timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        worksite = result.get('worksite', {})
                        worksite_id = worksite.get('id')
                        if worksite_id:
                            self.created_resources['worksites'].append(worksite_id)
                        self.log_result("Quote-to-Worksite Conversion", True, f"Quote converted to worksite: {worksite.get('title')}")
                    else:
                        self.log_result("Quote-to-Worksite Conversion", False, f"Conversion failed: {response.status_code}")
                else:
                    self.log_result("Quote-to-Worksite Conversion", False, f"Quote update failed: {response.status_code}")
            else:
                self.log_result("Quote-to-Worksite Conversion", False, "No quotes available for conversion")
        except Exception as e:
            self.log_result("Quote-to-Worksite Conversion", False, f"Error: {str(e)}")
        
        # Test 6.4: Worksite Management
        try:
            response = self.session.get(f"{BACKEND_URL}/worksites", timeout=10)
            
            if response.status_code == 200:
                worksites = response.json()
                self.log_result("Worksite Management", True, f"Retrieved {len(worksites)} worksites")
            else:
                self.log_result("Worksite Management", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Worksite Management", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all regression tests"""
        print("🚀 STARTING BACKEND REGRESSION TESTING AFTER FRONTEND UI FIXES")
        print("=" * 80)
        print("Testing Areas: Authentication, CRUD Operations, PDF Generation,")
        print("Statistics Dashboard, Search Management, Enhanced Features")
        print("=" * 80)
        
        # Setup sample data first
        self.setup_sample_data()
        
        # Run all test suites
        test_suites = [
            self.test_authentication_system,
            self.test_core_crud_operations,
            self.test_pdf_generation,
            self.test_statistics_dashboard,
            self.test_search_management,
            self.test_enhanced_features
        ]
        
        for test_suite in test_suites:
            try:
                test_suite()
            except Exception as e:
                suite_name = test_suite.__name__.replace('test_', '').replace('_', ' ').title()
                self.log_result(f"{suite_name} - Unexpected Error", False, f"Error: {str(e)}")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 BACKEND REGRESSION TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 50)
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   └─ {result['details']}")
        
        print("\n🎯 REGRESSION TESTING CONCLUSION:")
        print("-" * 50)
        if success_rate >= 95:
            print("✅ EXCELLENT: No regressions detected! All backend functionality intact.")
            print("   Frontend UI fixes did not impact backend APIs.")
        elif success_rate >= 85:
            print("✅ GOOD: Minor issues detected but core functionality working.")
            print("   Frontend changes had minimal impact on backend.")
        elif success_rate >= 70:
            print("⚠️  MODERATE: Some backend functionality affected.")
            print("   Investigation needed for failed tests.")
        else:
            print("❌ CRITICAL: Significant backend regressions detected!")
            print("   Immediate attention required.")
        
        # Categorize failed tests
        failed_tests_by_category = {}
        for result in self.test_results:
            if not result['success']:
                category = result['test'].split(' ')[0] if ' ' in result['test'] else 'Other'
                if category not in failed_tests_by_category:
                    failed_tests_by_category[category] = []
                failed_tests_by_category[category].append(result['test'])
        
        if failed_tests_by_category:
            print(f"\n❌ FAILED TESTS BY CATEGORY:")
            for category, tests in failed_tests_by_category.items():
                print(f"  {category}: {len(tests)} failed")
                for test in tests:
                    print(f"    - {test}")
        
        print(f"\n📊 CREATED RESOURCES DURING TESTING:")
        for resource_type, ids in self.created_resources.items():
            if ids:
                print(f"  - {resource_type}: {len(ids)} created")
        
        return success_rate >= 85  # Consider 85%+ as successful regression test

if __name__ == "__main__":
    tester = BackendRegressionTester()
    tester.run_all_tests()