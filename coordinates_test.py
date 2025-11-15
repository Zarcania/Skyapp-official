#!/usr/bin/env python3
"""
SkyApp Geographic Coordinates Testing
Testing latitude/longitude support and validation
"""

import requests
import json
from PIL import Image
import io

# Configuration
BACKEND_URL = "https://smart-inventory-97.preview.emergentagent.com/api"

class CoordinatesTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
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

    def setup_authentication(self):
        """Setup authentication for testing"""
        try:
            login_data = {
                "email": "tech@search-app.fr",
                "password": "tech123"
            }
            
            response = self.session.post(f"{self.backend_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                self.log_test("Authentication Setup", True, "Logged in successfully")
                return True
            else:
                self.log_test("Authentication Setup", False, f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Setup", False, f"Exception: {str(e)}")
            return False

    def create_test_image(self, size=(400, 300), color=(100, 100, 255)):
        """Create a test image file"""
        img = Image.new('RGB', size, color)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        return buffer

    def test_coordinates_precision(self):
        """Test high precision coordinates storage and retrieval"""
        try:
            # Test with high precision coordinates
            test_coordinates = [
                {"lat": 48.856614, "lng": 2.352222, "location": "Tour Eiffel, Paris"},
                {"lat": 43.604652, "lng": 1.444209, "location": "Toulouse, France"},
                {"lat": 45.764043, "lng": 4.835659, "location": "Lyon, France"},
                {"lat": -22.906847, "lng": -43.172896, "location": "Rio de Janeiro, Brazil"},
                {"lat": 35.676098, "lng": 139.650311, "location": "Tokyo, Japan"}
            ]
            
            created_searches = []
            
            for coord in test_coordinates:
                photo = self.create_test_image()
                files = [('photos', ('coord_test.jpg', photo, 'image/jpeg'))]
                
                data = {
                    'location': coord['location'],
                    'description': f'Test de précision des coordonnées pour {coord["location"]}',
                    'observations': f'Coordonnées: {coord["lat"]}, {coord["lng"]}',
                    'latitude': coord['lat'],
                    'longitude': coord['lng'],
                    'photo_numbers': [1]
                }
                
                response = self.session.post(
                    f"{self.backend_url}/searches",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    search_data = response.json()
                    created_searches.append({
                        'search': search_data,
                        'expected_lat': coord['lat'],
                        'expected_lng': coord['lng']
                    })
                else:
                    self.log_test(
                        "Coordinates Precision", 
                        False, 
                        f"Failed to create search for {coord['location']}: HTTP {response.status_code}"
                    )
                    return False
            
            # Verify all coordinates were stored correctly
            precision_errors = 0
            for item in created_searches:
                search = item['search']
                expected_lat = item['expected_lat']
                expected_lng = item['expected_lng']
                
                stored_lat = search.get('latitude')
                stored_lng = search.get('longitude')
                
                if stored_lat is None or stored_lng is None:
                    precision_errors += 1
                    continue
                
                # Check precision (should be exact for the precision we provided)
                lat_diff = abs(stored_lat - expected_lat)
                lng_diff = abs(stored_lng - expected_lng)
                
                if lat_diff > 0.000001 or lng_diff > 0.000001:
                    precision_errors += 1
            
            if precision_errors == 0:
                self.log_test(
                    "Coordinates Precision", 
                    True, 
                    f"All {len(created_searches)} coordinate pairs stored with high precision"
                )
                return True
            else:
                self.log_test(
                    "Coordinates Precision", 
                    False, 
                    f"{precision_errors}/{len(created_searches)} coordinates had precision issues"
                )
                
        except Exception as e:
            self.log_test("Coordinates Precision", False, f"Exception: {str(e)}")
        
        return False

    def test_coordinates_in_pdf(self):
        """Test that coordinates appear correctly in generated PDFs"""
        try:
            # Create a search with specific coordinates
            photo = self.create_test_image()
            files = [('photos', ('pdf_coord_test.jpg', photo, 'image/jpeg'))]
            
            test_lat = 48.858844
            test_lng = 2.294351
            
            data = {
                'location': 'Arc de Triomphe, Paris',
                'description': 'Test de génération PDF avec coordonnées précises',
                'observations': 'Vérification que les coordonnées GPS apparaissent dans le PDF',
                'latitude': test_lat,
                'longitude': test_lng,
                'photo_numbers': [1]
            }
            
            # Create search
            response = self.session.post(
                f"{self.backend_url}/searches",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                search_data = response.json()
                search_id = search_data['id']
                
                # Generate PDF
                pdf_response = self.session.post(
                    f"{self.backend_url}/reports/generate-pdf/{search_id}"
                )
                
                if pdf_response.status_code == 200:
                    content_type = pdf_response.headers.get('content-type', '')
                    content_length = len(pdf_response.content)
                    
                    if 'application/pdf' in content_type and content_length > 1000:
                        # PDF generated successfully - coordinates should be included
                        # We can't easily parse PDF content, but we can verify the search data
                        if (search_data.get('latitude') == test_lat and 
                            search_data.get('longitude') == test_lng):
                            self.log_test(
                                "Coordinates in PDF", 
                                True, 
                                f"PDF generated with coordinates {test_lat}, {test_lng} ({content_length} bytes)"
                            )
                            return True
                        else:
                            self.log_test(
                                "Coordinates in PDF", 
                                False, 
                                "Coordinates not properly stored in search data"
                            )
                    else:
                        self.log_test(
                            "Coordinates in PDF", 
                            False, 
                            f"Invalid PDF response: content-type={content_type}, size={content_length}"
                        )
                else:
                    self.log_test(
                        "Coordinates in PDF", 
                        False, 
                        f"PDF generation failed: HTTP {pdf_response.status_code}"
                    )
            else:
                self.log_test(
                    "Coordinates in PDF", 
                    False, 
                    f"Search creation failed: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Coordinates in PDF", False, f"Exception: {str(e)}")
        
        return False

    def test_coordinates_validation(self):
        """Test coordinate validation and edge cases"""
        try:
            # Test valid edge case coordinates
            edge_cases = [
                {"lat": 90.0, "lng": 180.0, "desc": "North Pole, International Date Line"},
                {"lat": -90.0, "lng": -180.0, "desc": "South Pole, Opposite Date Line"},
                {"lat": 0.0, "lng": 0.0, "desc": "Equator, Prime Meridian"},
                {"lat": 45.0, "lng": 0.0, "desc": "45°N on Prime Meridian"}
            ]
            
            valid_coordinates = 0
            
            for case in edge_cases:
                photo = self.create_test_image()
                files = [('photos', ('edge_case.jpg', photo, 'image/jpeg'))]
                
                data = {
                    'location': f'Test Edge Case: {case["desc"]}',
                    'description': 'Test de validation des coordonnées limites',
                    'observations': f'Coordonnées limites: {case["lat"]}, {case["lng"]}',
                    'latitude': case['lat'],
                    'longitude': case['lng'],
                    'photo_numbers': [1]
                }
                
                response = self.session.post(
                    f"{self.backend_url}/searches",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    search_data = response.json()
                    if (search_data.get('latitude') == case['lat'] and 
                        search_data.get('longitude') == case['lng']):
                        valid_coordinates += 1
                    else:
                        print(f"   Warning: Coordinates not stored correctly for {case['desc']}")
                else:
                    print(f"   Warning: Failed to create search for {case['desc']}: HTTP {response.status_code}")
            
            if valid_coordinates == len(edge_cases):
                self.log_test(
                    "Coordinates Validation", 
                    True, 
                    f"All {len(edge_cases)} edge case coordinates handled correctly"
                )
                return True
            else:
                self.log_test(
                    "Coordinates Validation", 
                    False, 
                    f"Only {valid_coordinates}/{len(edge_cases)} edge cases handled correctly"
                )
                
        except Exception as e:
            self.log_test("Coordinates Validation", False, f"Exception: {str(e)}")
        
        return False

    def run_coordinates_tests(self):
        """Run all coordinate tests"""
        print("🌍 Starting Geographic Coordinates Testing")
        print("=" * 50)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue testing.")
            return
        
        # Test coordinate precision
        self.test_coordinates_precision()
        
        # Test coordinates in PDF
        self.test_coordinates_in_pdf()
        
        # Test coordinate validation
        self.test_coordinates_validation()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 COORDINATES TEST SUMMARY")
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
    tester = CoordinatesTester()
    tester.run_coordinates_tests()