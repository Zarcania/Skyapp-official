#!/usr/bin/env python3
"""
SkyApp PDF Integration Test - Testing PDF generation with uploaded photos
"""

import requests
import json
import os
import tempfile
from PIL import Image
import io
from pathlib import Path
import time

# Configuration
BACKEND_URL = "https://smart-inventory-97.preview.emergentagent.com/api"

class PDFIntegrationTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def create_test_image(self, filename, size=(800, 600), color=(255, 0, 0)):
        """Create a test image file"""
        img = Image.new('RGB', size, color)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        return buffer

    def setup_authentication(self):
        """Setup authentication for testing"""
        try:
            # Login with test credentials
            login_data = {
                "email": "tech@search-app.fr",
                "password": "tech123"
            }
            
            response = self.session.post(f"{self.backend_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.test_user = data["user"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                self.log_test("Authentication Setup", True, f"Logged in as {self.test_user['email']}")
                return True
            else:
                self.log_test("Authentication Setup", False, f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Setup", False, f"Exception: {str(e)}")
            return False

    def test_pdf_generation_with_uploaded_photos(self):
        """Test PDF generation with photos that were uploaded via FormData"""
        try:
            # First, create a search with photos
            photo1 = self.create_test_image("pdf_test_1.jpg", (800, 600), (255, 100, 100))
            photo2 = self.create_test_image("pdf_test_2.jpg", (1024, 768), (100, 255, 100))
            
            files = [
                ('photos', ('pdf_test_1.jpg', photo1, 'image/jpeg')),
                ('photos', ('pdf_test_2.jpg', photo2, 'image/jpeg'))
            ]
            
            data = {
                'location': 'Site PDF Test avec Photos',
                'description': 'Test de génération PDF avec photos uploadées via FormData',
                'observations': 'Vérification que les photos apparaissent correctement dans le PDF généré',
                'latitude': 48.8566,
                'longitude': 2.3522,
                'photo_numbers': [1, 2]
            }
            
            # Create search with photos
            response = self.session.post(
                f"{self.backend_url}/searches",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                search_data = response.json()
                search_id = search_data['id']
                
                # Now test PDF generation for this search
                pdf_response = self.session.post(
                    f"{self.backend_url}/reports/generate-pdf/{search_id}"
                )
                
                if pdf_response.status_code == 200:
                    # Verify PDF content
                    content_type = pdf_response.headers.get('content-type', '')
                    content_length = len(pdf_response.content)
                    
                    if 'application/pdf' in content_type and content_length > 1000:
                        self.log_test(
                            "PDF Generation with Uploaded Photos", 
                            True, 
                            f"PDF generated successfully ({content_length} bytes) with uploaded photos"
                        )
                        return True
                    else:
                        self.log_test(
                            "PDF Generation with Uploaded Photos", 
                            False, 
                            f"Invalid PDF response: content-type={content_type}, size={content_length}"
                        )
                else:
                    self.log_test(
                        "PDF Generation with Uploaded Photos", 
                        False, 
                        f"PDF generation failed: HTTP {pdf_response.status_code}"
                    )
            else:
                self.log_test(
                    "PDF Generation with Uploaded Photos", 
                    False, 
                    f"Search creation failed: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("PDF Generation with Uploaded Photos", False, f"Exception: {str(e)}")
        
        return False

    def test_complete_workflow_end_to_end(self):
        """Test the complete workflow: Create → Store → Retrieve → PDF"""
        try:
            # Step 1: Create search with photos
            photo = self.create_test_image("workflow_test.jpg", (640, 480), (0, 100, 255))
            
            files = [('photos', ('workflow_test.jpg', photo, 'image/jpeg'))]
            data = {
                'location': 'Workflow Test Complet',
                'description': 'Test du workflow complet de bout en bout',
                'observations': 'Création → Stockage → Récupération → PDF',
                'latitude': 48.8566,
                'longitude': 2.3522,
                'photo_numbers': [1]
            }
            
            # Create search
            create_response = self.session.post(
                f"{self.backend_url}/searches",
                files=files,
                data=data
            )
            
            if create_response.status_code != 200:
                self.log_test("Complete Workflow End-to-End", False, "Search creation failed")
                return False
            
            search_data = create_response.json()
            search_id = search_data['id']
            
            # Step 2: Verify search appears in list
            list_response = self.session.get(f"{self.backend_url}/searches")
            if list_response.status_code != 200:
                self.log_test("Complete Workflow End-to-End", False, "Search listing failed")
                return False
            
            searches = list_response.json()
            found_search = None
            for search in searches:
                if search['id'] == search_id:
                    found_search = search
                    break
            
            if not found_search:
                self.log_test("Complete Workflow End-to-End", False, "Created search not found in list")
                return False
            
            # Step 3: Verify photo retrieval
            if found_search.get('photos') and len(found_search['photos']) > 0:
                photo_filename = found_search['photos'][0]['filename']
                photo_response = self.session.get(
                    f"{self.backend_url}/searches/{search_id}/photos/{photo_filename}"
                )
                
                if photo_response.status_code != 200:
                    self.log_test("Complete Workflow End-to-End", False, "Photo retrieval failed")
                    return False
            else:
                self.log_test("Complete Workflow End-to-End", False, "No photos found in search")
                return False
            
            # Step 4: Generate PDF
            pdf_response = self.session.post(
                f"{self.backend_url}/reports/generate-pdf/{search_id}"
            )
            
            if pdf_response.status_code != 200:
                self.log_test("Complete Workflow End-to-End", False, "PDF generation failed")
                return False
            
            # All steps successful
            self.log_test(
                "Complete Workflow End-to-End", 
                True, 
                "All workflow steps completed successfully: Create → List → Retrieve → PDF"
            )
            return True
            
        except Exception as e:
            self.log_test("Complete Workflow End-to-End", False, f"Exception: {str(e)}")
        
        return False

    def run_integration_tests(self):
        """Run PDF integration tests"""
        print("🔗 Starting PDF Integration Testing")
        print("=" * 50)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue testing.")
            return
        
        # Test PDF generation with uploaded photos
        self.test_pdf_generation_with_uploaded_photos()
        
        # Test complete workflow
        self.test_complete_workflow_end_to_end()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 PDF INTEGRATION TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"  • {result['test']}")

if __name__ == "__main__":
    tester = PDFIntegrationTester()
    tester.run_integration_tests()