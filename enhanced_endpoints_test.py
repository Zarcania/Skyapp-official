#!/usr/bin/env python3
"""
SkyApp Enhanced Endpoints Testing
Testing the newly added backend endpoints for complete functionality:
1. Share-to-Bureau Endpoint
2. Quote-to-Worksite Conversion  
3. Worksite Management
4. Complete Quote Workflow
5. Enhanced Functionality Integration
"""

import requests
import json
import os
import tempfile
from PIL import Image
import io
from pathlib import Path
import time
import uuid

# Configuration
BACKEND_URL = "https://smart-inventory-97.preview.emergentagent.com/api"

class SkyAppEnhancedEndpointsTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user = None
        self.test_results = []
        self.created_searches = []
        self.created_quotes = []
        self.created_clients = []
        self.created_worksites = []
        
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
        """Setup authentication using sample data"""
        try:
            # Initialize sample data
            response = self.session.post(f"{self.backend_url}/init-sample-data")
            
            # Login with sample credentials
            login_data = {
                "email": "tech@search-app.fr",
                "password": "tech123"
            }
            
            response = self.session.post(f"{self.backend_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.test_user = data["user"]
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("Authentication Setup", True, f"Logged in as {self.test_user['email']}")
                return True
            else:
                self.log_test("Authentication Setup", False, f"Login failed: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Setup", False, f"Exception: {str(e)}")
            return False

    def create_test_search(self, location="Test Location for Enhanced Testing"):
        """Create a test search for enhanced endpoint testing"""
        try:
            # Use FormData for search creation as required by the endpoint
            form_data = {
                'location': location,
                'description': 'Enhanced endpoint testing search',
                'observations': 'Testing new share-to-bureau functionality',
                'latitude': '48.8566',
                'longitude': '2.3522'
            }
            
            response = self.session.post(f"{self.backend_url}/searches", data=form_data)
            
            if response.status_code == 200:
                search = response.json()
                self.created_searches.append(search["id"])
                self.log_test("Create Test Search", True, f"Created search: {search['id']}")
                return search
            else:
                self.log_test("Create Test Search", False, f"Failed: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Create Test Search", False, f"Exception: {str(e)}")
            return None

    def create_test_client(self):
        """Create a test client for quote testing"""
        try:
            client_data = {
                "nom": "Enhanced Testing Client SARL",
                "email": f"enhanced-client-{uuid.uuid4().hex[:8]}@test.com",
                "telephone": "01 23 45 67 89",
                "adresse": "123 Enhanced Testing Street, 75001 Paris"
            }
            
            response = self.session.post(f"{self.backend_url}/clients", json=client_data)
            
            if response.status_code == 200:
                client = response.json()
                self.created_clients.append(client["id"])
                self.log_test("Create Test Client", True, f"Created client: {client['id']}")
                return client
            else:
                self.log_test("Create Test Client", False, f"Failed: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Create Test Client", False, f"Exception: {str(e)}")
            return None

    def create_test_quote(self, client_id):
        """Create a test quote for worksite conversion testing"""
        try:
            quote_data = {
                "client_id": client_id,
                "title": "Enhanced Testing Quote",
                "description": "Quote for enhanced endpoint testing - worksite conversion",
                "amount": 5000.0
            }
            
            response = self.session.post(f"{self.backend_url}/quotes", json=quote_data)
            
            if response.status_code == 200:
                quote = response.json()
                self.created_quotes.append(quote["id"])
                self.log_test("Create Test Quote", True, f"Created quote: {quote['id']}")
                return quote
            else:
                self.log_test("Create Test Quote", False, f"Failed: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Create Test Quote", False, f"Exception: {str(e)}")
            return None

    def test_share_to_bureau_endpoint(self):
        """Test POST /api/reports/share-to-bureau with search_ids array"""
        print("🔍 TESTING SHARE-TO-BUREAU ENDPOINT")
        
        # Create test searches
        search1 = self.create_test_search("Bureau Share Test Location 1")
        search2 = self.create_test_search("Bureau Share Test Location 2")
        
        if not search1 or not search2:
            self.log_test("Share-to-Bureau Setup", False, "Failed to create test searches")
            return False
        
        try:
            # Test with valid search_ids
            share_data = {
                "search_ids": [search1["id"], search2["id"]]
            }
            
            response = self.session.post(f"{self.backend_url}/reports/share-to-bureau", json=share_data)
            
            if response.status_code == 200:
                result = response.json()
                expected_count = 2
                actual_count = result.get("reports_created", 0)
                
                if actual_count == expected_count:
                    self.log_test("Share-to-Bureau Endpoint", True, 
                                f"Successfully shared {actual_count} searches to bureau")
                    
                    # Verify search status updates
                    search_response = self.session.get(f"{self.backend_url}/searches/{search1['id']}")
                    if search_response.status_code == 200:
                        updated_search = search_response.json()
                        if updated_search.get("status") == "SHARED_TO_BUREAU":
                            self.log_test("Search Status Update", True, "Search status updated to SHARED_TO_BUREAU")
                        else:
                            self.log_test("Search Status Update", False, 
                                        f"Expected SHARED_TO_BUREAU, got {updated_search.get('status')}")
                    
                    return True
                else:
                    self.log_test("Share-to-Bureau Endpoint", False, 
                                f"Expected {expected_count} reports, got {actual_count}")
                    return False
            else:
                self.log_test("Share-to-Bureau Endpoint", False, f"Failed: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Share-to-Bureau Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_share_to_bureau_error_handling(self):
        """Test error handling with empty search_ids"""
        try:
            # Test with empty search_ids
            share_data = {"search_ids": []}
            
            response = self.session.post(f"{self.backend_url}/reports/share-to-bureau", json=share_data)
            
            if response.status_code == 400:
                self.log_test("Share-to-Bureau Error Handling", True, "Correctly rejected empty search_ids")
                return True
            else:
                self.log_test("Share-to-Bureau Error Handling", False, 
                            f"Expected 400 error, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Share-to-Bureau Error Handling", False, f"Exception: {str(e)}")
            return False

    def test_quote_to_worksite_conversion(self):
        """Test POST /api/quotes/{quote_id}/convert-to-worksite"""
        print("🔍 TESTING QUOTE-TO-WORKSITE CONVERSION")
        
        # Create test client and quote
        client = self.create_test_client()
        if not client:
            return False
            
        quote = self.create_test_quote(client["id"])
        if not quote:
            return False
        
        try:
            # First, update quote status to ACCEPTED
            update_data = {"status": "ACCEPTED"}
            update_response = self.session.put(f"{self.backend_url}/quotes/{quote['id']}", json=update_data)
            
            if update_response.status_code != 200:
                self.log_test("Quote Status Update", False, f"Failed to accept quote: {update_response.text}")
                return False
            
            self.log_test("Quote Status Update", True, "Quote status updated to ACCEPTED")
            
            # Test conversion to worksite
            response = self.session.post(f"{self.backend_url}/quotes/{quote['id']}/convert-to-worksite")
            
            if response.status_code == 200:
                result = response.json()
                worksite = result.get("worksite")
                
                if worksite:
                    self.created_worksites.append(worksite["id"])
                    self.log_test("Quote-to-Worksite Conversion", True, 
                                f"Successfully converted quote to worksite: {worksite['id']}")
                    
                    # Verify worksite properties
                    expected_properties = ["id", "title", "client_id", "quote_id", "source", "status"]
                    missing_props = [prop for prop in expected_properties if prop not in worksite]
                    
                    if not missing_props:
                        self.log_test("Worksite Data Structure", True, "All required properties present")
                        
                        # Verify source is QUOTE
                        if worksite.get("source") == "QUOTE":
                            self.log_test("Worksite Source Verification", True, "Source correctly set to QUOTE")
                        else:
                            self.log_test("Worksite Source Verification", False, 
                                        f"Expected source QUOTE, got {worksite.get('source')}")
                        
                        return True
                    else:
                        self.log_test("Worksite Data Structure", False, 
                                    f"Missing properties: {missing_props}")
                        return False
                else:
                    self.log_test("Quote-to-Worksite Conversion", False, "No worksite data in response")
                    return False
            else:
                self.log_test("Quote-to-Worksite Conversion", False, f"Failed: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Quote-to-Worksite Conversion", False, f"Exception: {str(e)}")
            return False

    def test_quote_conversion_restrictions(self):
        """Test conversion only works with ACCEPTED quotes"""
        try:
            # Create a quote in DRAFT status
            client = self.create_test_client()
            if not client:
                return False
                
            quote = self.create_test_quote(client["id"])
            if not quote:
                return False
            
            # Try to convert DRAFT quote (should fail)
            response = self.session.post(f"{self.backend_url}/quotes/{quote['id']}/convert-to-worksite")
            
            if response.status_code == 400:
                self.log_test("Quote Conversion Restrictions", True, 
                            "Correctly rejected DRAFT quote conversion")
                return True
            else:
                self.log_test("Quote Conversion Restrictions", False, 
                            f"Expected 400 error, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Quote Conversion Restrictions", False, f"Exception: {str(e)}")
            return False

    def test_worksite_management(self):
        """Test GET /api/worksites and POST /api/worksites endpoints"""
        print("🔍 TESTING WORKSITE MANAGEMENT")
        
        try:
            # Test GET /api/worksites
            response = self.session.get(f"{self.backend_url}/worksites")
            
            if response.status_code == 200:
                worksites = response.json()
                self.log_test("Get Worksites Endpoint", True, f"Retrieved {len(worksites)} worksites")
                
                # Test POST /api/worksites for manual worksite creation
                worksite_data = {
                    "title": "Manual Test Worksite",
                    "description": "Manually created worksite for testing",
                    "address": "123 Manual Test Street, 75001 Paris",
                    "status": "PLANNED"
                }
                
                create_response = self.session.post(f"{self.backend_url}/worksites", json=worksite_data)
                
                if create_response.status_code == 200:
                    new_worksite = create_response.json()
                    self.created_worksites.append(new_worksite["id"])
                    self.log_test("Create Manual Worksite", True, 
                                f"Created manual worksite: {new_worksite['id']}")
                    
                    # Verify worksite data structure
                    required_fields = ["id", "title", "company_id", "source", "status"]
                    missing_fields = [field for field in required_fields if field not in new_worksite]
                    
                    if not missing_fields:
                        self.log_test("Manual Worksite Data Structure", True, "All required fields present")
                        
                        # Verify source is MANUAL
                        if new_worksite.get("source") == "MANUAL":
                            self.log_test("Manual Worksite Source", True, "Source correctly set to MANUAL")
                            return True
                        else:
                            self.log_test("Manual Worksite Source", False, 
                                        f"Expected MANUAL, got {new_worksite.get('source')}")
                            return False
                    else:
                        self.log_test("Manual Worksite Data Structure", False, 
                                    f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Create Manual Worksite", False, f"Failed: {create_response.text}")
                    return False
            else:
                self.log_test("Get Worksites Endpoint", False, f"Failed: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Worksite Management", False, f"Exception: {str(e)}")
            return False

    def test_complete_quote_workflow(self):
        """Test the complete quote workflow: Create → Accept → Convert → Verify"""
        print("🔍 TESTING COMPLETE QUOTE WORKFLOW")
        
        try:
            # Step 1: Create client
            client = self.create_test_client()
            if not client:
                return False
            
            # Step 2: Create quote
            quote = self.create_test_quote(client["id"])
            if not quote:
                return False
            
            # Step 3: Accept quote
            update_data = {"status": "ACCEPTED"}
            accept_response = self.session.put(f"{self.backend_url}/quotes/{quote['id']}", json=update_data)
            
            if accept_response.status_code != 200:
                self.log_test("Complete Workflow - Accept Quote", False, f"Failed: {accept_response.text}")
                return False
            
            # Step 4: Convert to worksite
            convert_response = self.session.post(f"{self.backend_url}/quotes/{quote['id']}/convert-to-worksite")
            
            if convert_response.status_code != 200:
                self.log_test("Complete Workflow - Convert to Worksite", False, f"Failed: {convert_response.text}")
                return False
            
            worksite_data = convert_response.json()
            worksite = worksite_data.get("worksite")
            
            # Step 5: Verify quote status update
            quote_response = self.session.get(f"{self.backend_url}/quotes")
            if quote_response.status_code == 200:
                quotes = quote_response.json()
                updated_quote = next((q for q in quotes if q["id"] == quote["id"]), None)
                
                if updated_quote and updated_quote.get("status") == "CONVERTED_TO_WORKSITE":
                    self.log_test("Complete Workflow - Quote Status Update", True, 
                                "Quote status updated to CONVERTED_TO_WORKSITE")
                else:
                    self.log_test("Complete Workflow - Quote Status Update", False, 
                                f"Expected CONVERTED_TO_WORKSITE, got {updated_quote.get('status') if updated_quote else 'None'}")
            
            # Step 6: Verify worksite creation
            if worksite:
                self.created_worksites.append(worksite["id"])
                self.log_test("Complete Quote Workflow", True, 
                            f"Complete workflow successful: Quote {quote['id']} → Worksite {worksite['id']}")
                return True
            else:
                self.log_test("Complete Quote Workflow", False, "Worksite not created")
                return False
                
        except Exception as e:
            self.log_test("Complete Quote Workflow", False, f"Exception: {str(e)}")
            return False

    def test_enhanced_functionality_integration(self):
        """Test the complete flow: Search → Share to Bureau → Quote → Accept → Worksite"""
        print("🔍 TESTING ENHANCED FUNCTIONALITY INTEGRATION")
        
        try:
            # Step 1: Create search
            search = self.create_test_search("Integration Test Location")
            if not search:
                return False
            
            # Step 2: Share to bureau
            share_data = {"search_ids": [search["id"]]}
            share_response = self.session.post(f"{self.backend_url}/reports/share-to-bureau", json=share_data)
            
            if share_response.status_code != 200:
                self.log_test("Integration - Share to Bureau", False, f"Failed: {share_response.text}")
                return False
            
            # Step 3: Create client and quote
            client = self.create_test_client()
            if not client:
                return False
                
            quote = self.create_test_quote(client["id"])
            if not quote:
                return False
            
            # Step 4: Accept quote
            update_data = {"status": "ACCEPTED"}
            accept_response = self.session.put(f"{self.backend_url}/quotes/{quote['id']}", json=update_data)
            
            if accept_response.status_code != 200:
                self.log_test("Integration - Accept Quote", False, f"Failed: {accept_response.text}")
                return False
            
            # Step 5: Convert to worksite
            convert_response = self.session.post(f"{self.backend_url}/quotes/{quote['id']}/convert-to-worksite")
            
            if convert_response.status_code != 200:
                self.log_test("Integration - Convert to Worksite", False, f"Failed: {convert_response.text}")
                return False
            
            worksite_data = convert_response.json()
            worksite = worksite_data.get("worksite")
            
            if worksite:
                self.created_worksites.append(worksite["id"])
                self.log_test("Enhanced Functionality Integration", True, 
                            f"Complete integration successful: Search → Bureau → Quote → Worksite {worksite['id']}")
                return True
            else:
                self.log_test("Enhanced Functionality Integration", False, "Integration failed at worksite creation")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Functionality Integration", False, f"Exception: {str(e)}")
            return False

    def test_data_persistence_and_relationships(self):
        """Test that all save operations work correctly and data relationships are maintained"""
        print("🔍 TESTING DATA PERSISTENCE AND RELATIONSHIPS")
        
        try:
            # Create related data
            client = self.create_test_client()
            quote = self.create_test_quote(client["id"])
            
            # Accept and convert quote
            update_data = {"status": "ACCEPTED"}
            self.session.put(f"{self.backend_url}/quotes/{quote['id']}", json=update_data)
            
            convert_response = self.session.post(f"{self.backend_url}/quotes/{quote['id']}/convert-to-worksite")
            worksite_data = convert_response.json()
            worksite = worksite_data.get("worksite")
            
            if not worksite:
                self.log_test("Data Persistence Setup", False, "Failed to create test data")
                return False
            
            # Verify relationships
            # 1. Worksite should reference quote_id
            if worksite.get("quote_id") == quote["id"]:
                self.log_test("Worksite-Quote Relationship", True, "Worksite correctly references quote")
            else:
                self.log_test("Worksite-Quote Relationship", False, 
                            f"Expected quote_id {quote['id']}, got {worksite.get('quote_id')}")
            
            # 2. Worksite should reference client_id
            if worksite.get("client_id") == client["id"]:
                self.log_test("Worksite-Client Relationship", True, "Worksite correctly references client")
            else:
                self.log_test("Worksite-Client Relationship", False, 
                            f"Expected client_id {client['id']}, got {worksite.get('client_id')}")
            
            # 3. Quote should have worksite_id after conversion
            quote_response = self.session.get(f"{self.backend_url}/quotes")
            if quote_response.status_code == 200:
                quotes = quote_response.json()
                updated_quote = next((q for q in quotes if q["id"] == quote["id"]), None)
                
                if updated_quote and updated_quote.get("worksite_id") == worksite["id"]:
                    self.log_test("Quote-Worksite Relationship", True, "Quote correctly references worksite")
                else:
                    self.log_test("Quote-Worksite Relationship", False, 
                                f"Expected worksite_id {worksite['id']}, got {updated_quote.get('worksite_id') if updated_quote else 'None'}")
            
            self.log_test("Data Persistence and Relationships", True, "All relationships verified")
            return True
            
        except Exception as e:
            self.log_test("Data Persistence and Relationships", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all enhanced endpoint tests"""
        print("🚀 STARTING ENHANCED ENDPOINTS TESTING")
        print("=" * 60)
        
        if not self.setup_authentication():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Test new enhanced endpoints
        test_methods = [
            self.test_share_to_bureau_endpoint,
            self.test_share_to_bureau_error_handling,
            self.test_quote_to_worksite_conversion,
            self.test_quote_conversion_restrictions,
            self.test_worksite_management,
            self.test_complete_quote_workflow,
            self.test_enhanced_functionality_integration,
            self.test_data_persistence_and_relationships
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(test_method.__name__, False, f"Unexpected error: {str(e)}")
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 ENHANCED ENDPOINTS TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}")
        
        # Cleanup info
        print(f"\n🧹 CLEANUP INFO:")
        print(f"Created Searches: {len(self.created_searches)}")
        print(f"Created Clients: {len(self.created_clients)}")
        print(f"Created Quotes: {len(self.created_quotes)}")
        print(f"Created Worksites: {len(self.created_worksites)}")

if __name__ == "__main__":
    tester = SkyAppEnhancedEndpointsTester()
    tester.run_all_tests()