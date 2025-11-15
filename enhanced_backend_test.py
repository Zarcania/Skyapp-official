#!/usr/bin/env python3
"""
Comprehensive Backend Testing for SkyApp Enhanced Functionalities
Testing all enhanced functionalities and save operations as requested in review.
"""

import requests
import json
import os
import tempfile
from datetime import datetime
import uuid
from pathlib import Path
from PIL import Image
import io

class SkyAppBackendTester:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://smart-inventory-97.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.auth_token = None
        self.test_user = None
        self.test_company_id = None
        self.test_results = []
        
        # Test data
        self.test_search_id = None
        self.test_client_id = None
        self.test_quote_id = None
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'status': status,
            'success': success,
            'details': details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def setup_authentication(self):
        """Setup authentication with sample data"""
        print("\n🔐 AUTHENTICATION SETUP")
        
        try:
            # Initialize sample data first
            response = self.session.post(f"{self.base_url}/init-sample-data")
            if response.status_code == 200:
                self.log_test("Sample Data Initialization", True, "Sample data created successfully")
            else:
                self.log_test("Sample Data Initialization", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Sample Data Initialization", False, f"Error: {str(e)}")
        
        # Login with sample credentials
        try:
            login_data = {
                "email": "tech@search-app.fr",
                "password": "tech123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data['access_token']
                self.test_user = data['user']
                self.test_company_id = self.test_user['company_id']
                
                # Set authorization header for all future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                self.log_test("Authentication Login", True, f"Logged in as {self.test_user['email']}")
                return True
            else:
                self.log_test("Authentication Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Login", False, f"Error: {str(e)}")
            return False
    
    def test_authentication_system(self):
        """Test 1: Authentication System"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        
        # Test /auth/me endpoint
        try:
            response = self.session.get(f"{self.base_url}/auth/me")
            if response.status_code == 200:
                user_data = response.json()
                self.log_test("JWT Token Validation (/auth/me)", True, f"User: {user_data.get('email')}")
            else:
                self.log_test("JWT Token Validation (/auth/me)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("JWT Token Validation (/auth/me)", False, f"Error: {str(e)}")
        
        # Test registration with new user
        try:
            register_data = {
                "company_name": f"Test Company {uuid.uuid4().hex[:8]}",
                "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                "nom": "Test",
                "prenom": "User",
                "password": "testpass123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=register_data)
            if response.status_code == 200:
                self.log_test("User Registration", True, "New user registered successfully")
            else:
                self.log_test("User Registration", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {str(e)}")
    
    def create_test_image(self, filename="test_photo.jpg"):
        """Create a test image for upload testing"""
        # Create a simple test image
        img = Image.new('RGB', (800, 600), color='blue')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        return img_buffer
    
    def test_search_operations(self):
        """Test 2: Search Operations with FormData and Photo Upload"""
        print("\n🔍 TESTING SEARCH OPERATIONS")
        
        # Test FormData search creation with photo upload
        try:
            # Create test images
            photo1 = self.create_test_image("photo1.jpg")
            
            # Prepare FormData
            files = {
                'photos': ('photo1.jpg', photo1, 'image/jpeg'),
            }
            
            data = {
                'location': 'Test Location for Enhanced Search',
                'description': 'Professional search with photo upload testing',
                'observations': 'Testing enhanced FormData functionality with photo uploads',
                'latitude': 48.8566,
                'longitude': 2.3522,
                'photo_numbers': [1, 2]
            }
            
            response = self.session.post(f"{self.base_url}/searches", files=files, data=data)
            
            if response.status_code == 200:
                search_data = response.json()
                self.test_search_id = search_data['id']
                self.log_test("FormData Search Creation with Photos", True, f"Search ID: {self.test_search_id}")
                
                # Verify photos were uploaded
                if search_data.get('photos') and len(search_data['photos']) > 0:
                    self.log_test("Photo Upload Verification", True, f"Photos uploaded: {len(search_data['photos'])}")
                else:
                    self.log_test("Photo Upload Verification", False, "No photos found in response")
            else:
                self.log_test("FormData Search Creation with Photos", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("FormData Search Creation with Photos", False, f"Error: {str(e)}")
        
        # Test search listing
        try:
            response = self.session.get(f"{self.base_url}/searches")
            if response.status_code == 200:
                searches = response.json()
                self.log_test("Search Listing", True, f"Found {len(searches)} searches")
                
                # Use first search if we don't have test_search_id
                if not self.test_search_id and searches:
                    self.test_search_id = searches[0]['id']
            else:
                self.log_test("Search Listing", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Search Listing", False, f"Error: {str(e)}")
        
        # Test search editing (PUT /api/searches/{id})
        if self.test_search_id:
            try:
                update_data = {
                    "location": "Updated Location - Enhanced Testing",
                    "description": "Updated description for enhanced functionality testing",
                    "observations": "Updated observations with enhanced features",
                    "latitude": 48.8570,
                    "longitude": 2.3525
                }
                
                response = self.session.put(f"{self.base_url}/searches/{self.test_search_id}", json=update_data)
                if response.status_code == 200:
                    self.log_test("Search Edit Functionality (PUT)", True, "Search updated successfully")
                else:
                    self.log_test("Search Edit Functionality (PUT)", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Search Edit Functionality (PUT)", False, f"Error: {str(e)}")
        
        # Test search status update
        if self.test_search_id:
            try:
                response = self.session.put(
                    f"{self.base_url}/searches/{self.test_search_id}/status",
                    data="SHARED",
                    headers={'Content-Type': 'text/plain'}
                )
                if response.status_code == 200:
                    self.log_test("Search Status Update", True, "Status updated to SHARED")
                else:
                    self.log_test("Search Status Update", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Search Status Update", False, f"Error: {str(e)}")
    
    def test_pdf_generation_system(self):
        """Test 3: PDF Generation System"""
        print("\n📄 TESTING PDF GENERATION SYSTEM")
        
        if not self.test_search_id:
            self.log_test("PDF Generation - No Search ID", False, "No search ID available for testing")
            return
        
        # Test individual search PDF generation
        try:
            response = self.session.post(f"{self.base_url}/reports/generate-pdf/{self.test_search_id}")
            if response.status_code == 200:
                # Check if response is PDF
                if response.headers.get('content-type') == 'application/pdf':
                    pdf_size = len(response.content)
                    self.log_test("Individual Search PDF Generation", True, f"PDF generated, size: {pdf_size} bytes")
                else:
                    self.log_test("Individual Search PDF Generation", False, "Response is not a PDF")
            else:
                self.log_test("Individual Search PDF Generation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Individual Search PDF Generation", False, f"Error: {str(e)}")
        
        # Test summary PDF generation for multiple searches
        try:
            # Get available searches first
            searches_response = self.session.get(f"{self.base_url}/searches")
            if searches_response.status_code == 200:
                searches = searches_response.json()
                search_ids = [search['id'] for search in searches[:3]]  # Take first 3 searches
                
                summary_data = {"search_ids": search_ids}
                response = self.session.post(f"{self.base_url}/reports/generate-summary-pdf", json=summary_data)
                
                if response.status_code == 200:
                    if response.headers.get('content-type') == 'application/pdf':
                        pdf_size = len(response.content)
                        self.log_test("Summary PDF Generation", True, f"Summary PDF generated, size: {pdf_size} bytes")
                    else:
                        self.log_test("Summary PDF Generation", False, "Response is not a PDF")
                else:
                    self.log_test("Summary PDF Generation", False, f"Status: {response.status_code}")
            else:
                self.log_test("Summary PDF Generation", False, "Could not get searches for summary")
        except Exception as e:
            self.log_test("Summary PDF Generation", False, f"Error: {str(e)}")
        
        # Test share-to-bureau endpoint (if it exists)
        try:
            if self.test_search_id:
                response = self.session.post(f"{self.base_url}/reports/share-to-bureau", json={"search_id": self.test_search_id})
                if response.status_code == 200:
                    self.log_test("Share-to-Bureau Endpoint", True, "Share to bureau successful")
                elif response.status_code == 404:
                    self.log_test("Share-to-Bureau Endpoint", False, "Endpoint not implemented (404)")
                else:
                    self.log_test("Share-to-Bureau Endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Share-to-Bureau Endpoint", False, f"Error: {str(e)}")
    
    def test_enhanced_quote_system(self):
        """Test 4: Enhanced Quote System"""
        print("\n💰 TESTING ENHANCED QUOTE SYSTEM")
        
        # First create a client for the quote
        try:
            client_data = {
                "nom": "Enhanced Test Client",
                "email": f"client_{uuid.uuid4().hex[:8]}@example.com",
                "telephone": "01 23 45 67 89",
                "adresse": "123 Test Street, Enhanced City"
            }
            
            response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if response.status_code == 200:
                client = response.json()
                self.test_client_id = client['id']
                self.log_test("Client Creation for Quote", True, f"Client ID: {self.test_client_id}")
            else:
                self.log_test("Client Creation for Quote", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Client Creation for Quote", False, f"Error: {str(e)}")
        
        # Test quote creation with optional fields
        if self.test_client_id:
            try:
                quote_data = {
                    "client_id": self.test_client_id,
                    "title": "Enhanced Quote with Optional Fields",
                    "description": "Professional quote testing with enhanced functionality",
                    "amount": 2500.00
                }
                
                response = self.session.post(f"{self.base_url}/quotes", json=quote_data)
                if response.status_code == 200:
                    quote = response.json()
                    self.test_quote_id = quote['id']
                    self.log_test("Quote Creation with Optional Fields", True, f"Quote ID: {self.test_quote_id}")
                else:
                    self.log_test("Quote Creation with Optional Fields", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Quote Creation with Optional Fields", False, f"Error: {str(e)}")
        
        # Test quote status updates (accept/reject workflow)
        if self.test_quote_id:
            try:
                # Test quote update (status change)
                update_data = {
                    "status": "ACCEPTED",
                    "title": "Updated Enhanced Quote",
                    "amount": 2750.00
                }
                
                response = self.session.put(f"{self.base_url}/quotes/{self.test_quote_id}", json=update_data)
                if response.status_code == 200:
                    self.log_test("Quote Status Update (Accept/Reject)", True, "Quote status updated to ACCEPTED")
                else:
                    self.log_test("Quote Status Update (Accept/Reject)", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Quote Status Update (Accept/Reject)", False, f"Error: {str(e)}")
        
        # Test quote-to-worksite transformation (if endpoint exists)
        try:
            if self.test_quote_id:
                worksite_data = {
                    "quote_id": self.test_quote_id,
                    "scheduled_date": "2024-02-15",
                    "location": "Enhanced Worksite Location",
                    "description": "Worksite created from enhanced quote"
                }
                
                response = self.session.post(f"{self.base_url}/worksites", json=worksite_data)
                if response.status_code == 200:
                    self.log_test("Quote-to-Worksite Transformation", True, "Worksite created from quote")
                elif response.status_code == 404:
                    self.log_test("Quote-to-Worksite Transformation", False, "Worksite endpoint not found (404)")
                else:
                    self.log_test("Quote-to-Worksite Transformation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Quote-to-Worksite Transformation", False, f"Error: {str(e)}")
    
    def test_client_management(self):
        """Test 5: Client Management"""
        print("\n👥 TESTING CLIENT MANAGEMENT")
        
        # Test quick client addition
        try:
            client_data = {
                "nom": "Quick Add Client",
                "email": f"quickadd_{uuid.uuid4().hex[:8]}@example.com",
                "telephone": "01 98 76 54 32"
            }
            
            response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if response.status_code == 200:
                client = response.json()
                self.log_test("Quick Client Addition", True, f"Client ID: {client['id']}")
                
                # Test client update
                update_data = {
                    "nom": "Updated Quick Client",
                    "adresse": "456 Updated Street, New City"
                }
                
                update_response = self.session.put(f"{self.base_url}/clients/{client['id']}", json=update_data)
                if update_response.status_code == 200:
                    self.log_test("Client Update", True, "Client updated successfully")
                else:
                    self.log_test("Client Update", False, f"Status: {update_response.status_code}")
                    
            else:
                self.log_test("Quick Client Addition", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Quick Client Addition", False, f"Error: {str(e)}")
        
        # Test client listing
        try:
            response = self.session.get(f"{self.base_url}/clients")
            if response.status_code == 200:
                clients = response.json()
                self.log_test("Client Listing", True, f"Found {len(clients)} clients")
            else:
                self.log_test("Client Listing", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Client Listing", False, f"Error: {str(e)}")
    
    def test_new_backend_endpoints(self):
        """Test 6: New Backend Endpoints"""
        print("\n🔗 TESTING NEW BACKEND ENDPOINTS")
        
        # Test /api/worksites endpoint
        try:
            worksite_data = {
                "name": "Enhanced Test Worksite",
                "location": "Test Worksite Location",
                "scheduled_date": "2024-02-20",
                "description": "Testing new worksite endpoint",
                "status": "PLANNED"
            }
            
            response = self.session.post(f"{self.base_url}/sites", json=worksite_data)  # Using /sites as per server.py
            if response.status_code == 200:
                worksite = response.json()
                self.log_test("Worksite Creation (/api/sites)", True, f"Worksite ID: {worksite['id']}")
                
                # Test worksite listing
                list_response = self.session.get(f"{self.base_url}/sites")
                if list_response.status_code == 200:
                    worksites = list_response.json()
                    self.log_test("Worksite Listing", True, f"Found {len(worksites)} worksites")
                else:
                    self.log_test("Worksite Listing", False, f"Status: {list_response.status_code}")
                    
            else:
                self.log_test("Worksite Creation (/api/sites)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Worksite Creation (/api/sites)", False, f"Error: {str(e)}")
        
        # Test invitation management endpoints
        try:
            invitation_data = {
                "email": f"invite_{uuid.uuid4().hex[:8]}@example.com",
                "role": "TECHNICIEN",
                "message": "Welcome to our enhanced team!"
            }
            
            response = self.session.post(f"{self.base_url}/invitations", json=invitation_data)
            if response.status_code == 200:
                invitation = response.json()
                self.log_test("Invitation Creation", True, f"Invitation ID: {invitation['id']}")
                
                # Test invitation listing
                list_response = self.session.get(f"{self.base_url}/invitations")
                if list_response.status_code == 200:
                    invitations = list_response.json()
                    self.log_test("Invitation Listing", True, f"Found {len(invitations)} invitations")
                else:
                    self.log_test("Invitation Listing", False, f"Status: {list_response.status_code}")
                    
            else:
                self.log_test("Invitation Creation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Invitation Creation", False, f"Error: {str(e)}")
    
    def test_file_upload_storage(self):
        """Test 7: File Upload & Storage"""
        print("\n📁 TESTING FILE UPLOAD & STORAGE")
        
        if not self.test_search_id:
            self.log_test("File Upload Testing - No Search ID", False, "No search ID available")
            return
        
        # Test photo serving endpoint
        try:
            # First get search details to see if it has photos
            response = self.session.get(f"{self.base_url}/searches/{self.test_search_id}")
            if response.status_code == 200:
                search_data = response.json()
                photos = search_data.get('photos', [])
                
                if photos:
                    # Try to access the first photo
                    first_photo = photos[0]
                    photo_filename = first_photo.get('filename')
                    
                    if photo_filename:
                        photo_response = self.session.get(f"{self.base_url}/searches/{self.test_search_id}/photos/{photo_filename}")
                        if photo_response.status_code == 200:
                            self.log_test("Photo Serving Endpoint", True, f"Photo served successfully: {photo_filename}")
                        else:
                            self.log_test("Photo Serving Endpoint", False, f"Status: {photo_response.status_code}")
                    else:
                        self.log_test("Photo Serving Endpoint", False, "No photo filename found")
                else:
                    self.log_test("Photo Serving Endpoint", False, "No photos found in search")
            else:
                self.log_test("Photo Serving Endpoint", False, f"Could not get search details: {response.status_code}")
        except Exception as e:
            self.log_test("Photo Serving Endpoint", False, f"Error: {str(e)}")
        
        # Test file storage verification (indirect through search creation)
        try:
            # Create another search with photo to test storage
            photo = self.create_test_image("storage_test.jpg")
            
            files = {'photos': ('storage_test.jpg', photo, 'image/jpeg')}
            data = {
                'location': 'Storage Test Location',
                'description': 'Testing file storage functionality',
                'latitude': 48.8566,
                'longitude': 2.3522
            }
            
            response = self.session.post(f"{self.base_url}/searches", files=files, data=data)
            if response.status_code == 200:
                search_data = response.json()
                if search_data.get('photos') and len(search_data['photos']) > 0:
                    self.log_test("File Storage Verification", True, "Files stored successfully in backend")
                else:
                    self.log_test("File Storage Verification", False, "No photos found after upload")
            else:
                self.log_test("File Storage Verification", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("File Storage Verification", False, f"Error: {str(e)}")
    
    def test_data_consistency(self):
        """Test 8: Data Consistency"""
        print("\n🔄 TESTING DATA CONSISTENCY")
        
        # Test save operations persist correctly
        try:
            # Create a search and verify it persists
            search_data = {
                'location': 'Consistency Test Location',
                'description': 'Testing data persistence and consistency',
                'observations': 'Verifying all save operations work correctly',
                'latitude': 48.8566,
                'longitude': 2.3522
            }
            
            # Create search
            create_response = self.session.post(f"{self.base_url}/searches", data=search_data)
            if create_response.status_code == 200:
                created_search = create_response.json()
                search_id = created_search['id']
                
                # Verify it can be retrieved
                get_response = self.session.get(f"{self.base_url}/searches/{search_id}")
                if get_response.status_code == 200:
                    retrieved_search = get_response.json()
                    
                    # Check data consistency
                    if (retrieved_search['location'] == search_data['location'] and
                        retrieved_search['description'] == search_data['description']):
                        self.log_test("Data Persistence Verification", True, "Search data persisted correctly")
                    else:
                        self.log_test("Data Persistence Verification", False, "Data mismatch after save")
                else:
                    self.log_test("Data Persistence Verification", False, f"Could not retrieve saved search: {get_response.status_code}")
            else:
                self.log_test("Data Persistence Verification", False, f"Could not create search: {create_response.status_code}")
        except Exception as e:
            self.log_test("Data Persistence Verification", False, f"Error: {str(e)}")
        
        # Test UUID consistency
        try:
            response = self.session.get(f"{self.base_url}/searches")
            if response.status_code == 200:
                searches = response.json()
                uuid_consistent = True
                
                for search in searches[:5]:  # Check first 5 searches
                    search_id = search.get('id')
                    if not search_id or len(search_id) != 36:  # UUID should be 36 characters
                        uuid_consistent = False
                        break
                
                if uuid_consistent:
                    self.log_test("UUID Consistency", True, "All UUIDs are properly formatted")
                else:
                    self.log_test("UUID Consistency", False, "Some UUIDs are not properly formatted")
            else:
                self.log_test("UUID Consistency", False, f"Could not get searches: {response.status_code}")
        except Exception as e:
            self.log_test("UUID Consistency", False, f"Error: {str(e)}")
        
        # Test data relationships
        try:
            # Get searches and verify they belong to the correct company
            response = self.session.get(f"{self.base_url}/searches")
            if response.status_code == 200:
                searches = response.json()
                relationship_consistent = True
                
                for search in searches[:3]:  # Check first 3 searches
                    if search.get('company_id') != self.test_company_id:
                        relationship_consistent = False
                        break
                
                if relationship_consistent:
                    self.log_test("Data Relationships", True, "Company relationships are consistent")
                else:
                    self.log_test("Data Relationships", False, "Company relationship inconsistencies found")
            else:
                self.log_test("Data Relationships", False, f"Could not verify relationships: {response.status_code}")
        except Exception as e:
            self.log_test("Data Relationships", False, f"Error: {str(e)}")
    
    def test_enhanced_statistics_dashboard(self):
        """Test Enhanced Statistics Dashboard"""
        print("\n📊 TESTING ENHANCED STATISTICS DASHBOARD")
        
        try:
            response = self.session.get(f"{self.base_url}/stats/dashboard")
            if response.status_code == 200:
                stats = response.json()
                
                # Check for required enhanced metrics
                required_metrics = ['total_searches', 'total_reports', 'total_clients', 'total_quotes', 'total_users', 'recent_searches']
                missing_metrics = [metric for metric in required_metrics if metric not in stats]
                
                if not missing_metrics:
                    self.log_test("Enhanced Statistics Dashboard", True, f"All enhanced metrics present: {list(stats.keys())}")
                else:
                    self.log_test("Enhanced Statistics Dashboard", False, f"Missing metrics: {missing_metrics}")
            else:
                self.log_test("Enhanced Statistics Dashboard", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Enhanced Statistics Dashboard", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all enhanced functionality tests"""
        print("🚀 STARTING COMPREHENSIVE SKYAPP BACKEND TESTING")
        print("=" * 60)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Run all test suites
        self.test_authentication_system()
        self.test_search_operations()
        self.test_pdf_generation_system()
        self.test_enhanced_quote_system()
        self.test_client_management()
        self.test_new_backend_endpoints()
        self.test_file_upload_storage()
        self.test_data_consistency()
        self.test_enhanced_statistics_dashboard()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📊 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details'] and not result['success']:
                print(f"   ⚠️  {result['details']}")
        
        print("\n" + "=" * 60)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: All enhanced functionalities are working properly!")
        elif success_rate >= 75:
            print("✅ GOOD: Most enhanced functionalities are working with minor issues.")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Some enhanced functionalities need attention.")
        else:
            print("❌ CRITICAL: Major issues found with enhanced functionalities.")

if __name__ == "__main__":
    tester = SkyAppBackendTester()
    tester.run_all_tests()