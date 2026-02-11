#!/usr/bin/env python3
"""
Technicien Search Creation and Retrieval Workflow Test
Testing the complete workflow: Create Search → Save to Database → Retrieve in History
"""

import requests
import json
import os
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://smart-inventory-97.preview.emergentagent.com/api"

# Test credentials for Technicien user
TECHNICIEN_EMAIL = "tech@search-app.fr"
TECHNICIEN_PASSWORD = "tech123"

class TechnicienSearchWorkflowTest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_info = None
        self.test_search_id = None
        
    def authenticate_technicien(self):
        """Authenticate as Technicien user"""
        print("🔐 Authenticating Technicien user...")
        
        login_data = {
            "email": TECHNICIEN_EMAIL,
            "password": TECHNICIEN_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                auth_data = response.json()
                self.auth_token = auth_data["access_token"]
                self.user_info = auth_data["user"]
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Authentication successful for {self.user_info['prenom']} {self.user_info['nom']}")
                print(f"   Role: {self.user_info['role']}")
                print(f"   Company ID: {self.user_info['company_id']}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_search_creation(self):
        """Test POST /api/searches endpoint with form data"""
        print("\n📝 Testing Search Creation...")
        
        # Prepare realistic search data
        search_data = {
            "location": "Chantier Rue de la République, 75011 Paris",
            "description": "Recherche de canalisations d'eau potable avant travaux de voirie. Zone résidentielle avec commerces au rez-de-chaussée.",
            "observations": "Sol pavé ancien, présence de réseaux électriques et gaz à proximité. Accès difficile côté nord.",
            "latitude": 48.8566,
            "longitude": 2.3522
        }
        
        try:
            # Test with form data (multipart/form-data)
            response = self.session.post(f"{BACKEND_URL}/searches", data=search_data)
            
            if response.status_code == 200:
                search_result = response.json()
                self.test_search_id = search_result["id"]
                
                print("✅ Search creation successful!")
                print(f"   Search ID: {self.test_search_id}")
                print(f"   Location: {search_result['location']}")
                print(f"   Description: {search_result['description'][:50]}...")
                print(f"   Status: {search_result['status']}")
                print(f"   Created at: {search_result['created_at']}")
                print(f"   User ID: {search_result['user_id']}")
                print(f"   Company ID: {search_result['company_id']}")
                
                # Verify required fields are present
                required_fields = ['id', 'location', 'description', 'user_id', 'company_id', 'status', 'created_at']
                missing_fields = [field for field in required_fields if field not in search_result]
                
                if missing_fields:
                    print(f"⚠️  Missing required fields: {missing_fields}")
                    return False
                
                # Verify user and company isolation
                if search_result['user_id'] != self.user_info['id']:
                    print(f"❌ User ID mismatch: expected {self.user_info['id']}, got {search_result['user_id']}")
                    return False
                
                if search_result['company_id'] != self.user_info['company_id']:
                    print(f"❌ Company ID mismatch: expected {self.user_info['company_id']}, got {search_result['company_id']}")
                    return False
                
                print("✅ Search data validation passed")
                return True
                
            else:
                print(f"❌ Search creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Search creation error: {str(e)}")
            return False
    
    def test_search_retrieval(self):
        """Test GET /api/searches endpoint to retrieve all searches"""
        print("\n📋 Testing Search Retrieval...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/searches")
            
            if response.status_code == 200:
                searches = response.json()
                
                print(f"✅ Search retrieval successful!")
                print(f"   Total searches found: {len(searches)}")
                
                if not searches:
                    print("⚠️  No searches found")
                    return False
                
                # Verify our test search is in the results
                test_search_found = False
                for search in searches:
                    if search['id'] == self.test_search_id:
                        test_search_found = True
                        print(f"✅ Test search found in results:")
                        print(f"   ID: {search['id']}")
                        print(f"   Location: {search['location']}")
                        print(f"   Status: {search['status']}")
                        break
                
                if not test_search_found:
                    print(f"❌ Test search {self.test_search_id} not found in results")
                    return False
                
                # Verify searches are ordered by most recent first
                if len(searches) > 1:
                    first_search_date = datetime.fromisoformat(searches[0]['created_at'].replace('Z', '+00:00'))
                    second_search_date = datetime.fromisoformat(searches[1]['created_at'].replace('Z', '+00:00'))
                    
                    if first_search_date >= second_search_date:
                        print("✅ Searches are properly ordered (most recent first)")
                    else:
                        print("⚠️  Searches may not be properly ordered")
                
                # Verify all searches belong to current user/company
                for search in searches:
                    if search['user_id'] != self.user_info['id']:
                        print(f"❌ Found search from different user: {search['id']}")
                        return False
                    if search['company_id'] != self.user_info['company_id']:
                        print(f"❌ Found search from different company: {search['id']}")
                        return False
                
                print("✅ Company-based isolation verified")
                return True
                
            else:
                print(f"❌ Search retrieval failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Search retrieval error: {str(e)}")
            return False
    
    def test_search_history_verification(self):
        """Verify search history features and metadata"""
        print("\n🔍 Testing Search History Verification...")
        
        try:
            # Get specific search details
            response = self.session.get(f"{BACKEND_URL}/searches/{self.test_search_id}")
            
            if response.status_code == 200:
                search = response.json()
                
                print("✅ Individual search retrieval successful!")
                
                # Verify search reference (ID) is properly generated
                search_ref = search['id']
                if len(search_ref) >= 8:  # UUID should be longer than 8 chars
                    print(f"✅ Search reference generated: {search_ref[:8].upper()}")
                else:
                    print(f"⚠️  Search reference may be invalid: {search_ref}")
                
                # Verify metadata is properly stored
                metadata_fields = ['created_at', 'status', 'user_id', 'company_id']
                for field in metadata_fields:
                    if field in search:
                        print(f"✅ Metadata field '{field}': {search[field]}")
                    else:
                        print(f"❌ Missing metadata field: {field}")
                        return False
                
                # Verify status management
                if search['status'] in ['ACTIVE', 'SHARED', 'SHARED_TO_BUREAU', 'PROCESSED', 'ARCHIVED']:
                    print(f"✅ Valid search status: {search['status']}")
                else:
                    print(f"⚠️  Unexpected search status: {search['status']}")
                
                # Verify coordinates are stored (default Paris coordinates if not provided)
                if 'latitude' in search and 'longitude' in search:
                    print(f"✅ GPS coordinates stored: {search['latitude']}, {search['longitude']}")
                else:
                    print("⚠️  GPS coordinates missing")
                
                return True
                
            else:
                print(f"❌ Individual search retrieval failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Search history verification error: {str(e)}")
            return False
    
    def test_search_status_update(self):
        """Test search status update functionality"""
        print("\n🔄 Testing Search Status Update...")
        
        try:
            # Update search status to SHARED
            new_status = "SHARED"
            response = self.session.put(
                f"{BACKEND_URL}/searches/{self.test_search_id}/status",
                data=new_status,
                headers={"Content-Type": "text/plain"}
            )
            
            if response.status_code == 200:
                print(f"✅ Status update successful to: {new_status}")
                
                # Verify status was updated
                verify_response = self.session.get(f"{BACKEND_URL}/searches/{self.test_search_id}")
                if verify_response.status_code == 200:
                    updated_search = verify_response.json()
                    if updated_search['status'] == new_status:
                        print("✅ Status update verified in database")
                        return True
                    else:
                        print(f"❌ Status not updated: expected {new_status}, got {updated_search['status']}")
                        return False
                else:
                    print("❌ Could not verify status update")
                    return False
            else:
                print(f"❌ Status update failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Status update error: {str(e)}")
            return False
    
    def run_complete_workflow_test(self):
        """Run the complete Technicien search workflow test"""
        print("🚀 Starting Technicien Search Creation and Retrieval Workflow Test")
        print("=" * 70)
        
        test_results = []
        
        # Step 1: Authentication
        if self.authenticate_technicien():
            test_results.append(("Authentication", True))
        else:
            test_results.append(("Authentication", False))
            return self.print_final_results(test_results)
        
        # Step 2: Search Creation
        if self.test_search_creation():
            test_results.append(("Search Creation", True))
        else:
            test_results.append(("Search Creation", False))
            return self.print_final_results(test_results)
        
        # Step 3: Search Retrieval
        if self.test_search_retrieval():
            test_results.append(("Search Retrieval", True))
        else:
            test_results.append(("Search Retrieval", False))
        
        # Step 4: Search History Verification
        if self.test_search_history_verification():
            test_results.append(("Search History Verification", True))
        else:
            test_results.append(("Search History Verification", False))
        
        # Step 5: Search Status Update
        if self.test_search_status_update():
            test_results.append(("Search Status Update", True))
        else:
            test_results.append(("Search Status Update", False))
        
        return self.print_final_results(test_results)
    
    def print_final_results(self, test_results):
        """Print final test results summary"""
        print("\n" + "=" * 70)
        print("📊 TECHNICIEN SEARCH WORKFLOW TEST RESULTS")
        print("=" * 70)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<30} {status}")
            if result:
                passed_tests += 1
        
        print("-" * 70)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED! Technicien search workflow is working perfectly!")
        elif success_rate >= 80:
            print("✅ Most tests passed. Minor issues may need attention.")
        else:
            print("❌ Multiple test failures. Significant issues need to be addressed.")
        
        print("=" * 70)
        return success_rate >= 80

if __name__ == "__main__":
    tester = TechnicienSearchWorkflowTest()
    tester.run_complete_workflow_test()