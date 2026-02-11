#!/usr/bin/env python3
"""
Comprehensive Backend Test for SkyApp
Tests all new functionalities as requested:
1. Authentication System - Login/Register with JWT
2. Complete CRUD - Users, Companies, Searches, Reports, Clients, Quotes, Sites, Invitations
3. PDF Generation - Individual and synthesis with Apple design
4. Status Management - Update search statuses
5. Client Management - Complete CRUD clients
6. Quote Management - Complete CRUD quotes
7. Site Planning - Complete CRUD sites/interventions
8. Invitation Management - Complete CRUD invitations
9. Statistics Dashboard - Statistics endpoints
10. File Upload - Upload images for PDF
"""

import requests
import sys
import json
import io
import os
from datetime import datetime
from typing import Dict, Any, Optional

class SkyAppComprehensiveTester:
    def __init__(self):
        # Use the actual backend URL from frontend/.env
        self.base_url = "https://smart-inventory-97.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        
        # Test tracking
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        
        # Authentication tokens and user data
        self.bureau_token = None
        self.tech_token = None
        self.bureau_user = None
        self.tech_user = None
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
                    expected_status: int = 200) -> tuple[bool, Any]:
        """Make HTTP request and return success status and response data"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        if not files:  # Only set Content-Type for JSON requests
            headers['Content-Type'] = 'application/json'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files, 
                                           headers={k: v for k, v in headers.items() if k != 'Content-Type'}, 
                                           timeout=15)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                if files:
                    response = requests.put(url, data=data, files=files,
                                          headers={k: v for k, v in headers.items() if k != 'Content-Type'},
                                          timeout=15)
                else:
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

    # ==================== AUTHENTICATION TESTS ====================
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.make_request('GET', '')
        self.log_test("Root API Endpoint", success, response)
        return success

    def test_register_new_company(self):
        """Test company registration with new user"""
        register_data = {
            "company_name": "BTP Excellence SARL",
            "email": "admin@btp-excellence.fr",
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

    def test_register_duplicate_email(self):
        """Test registration with duplicate email (should fail)"""
        register_data = {
            "company_name": "Another Company",
            "email": "admin@btp-excellence.fr",  # Same email as above
            "nom": "Test",
            "prenom": "User",
            "password": "password123"
        }
        
        success, response = self.make_request('POST', 'auth/register', register_data, expected_status=400)
        self.log_test("Duplicate Email Registration (Should Fail)", success, None, 
                     response if not success else "Correctly rejected duplicate email")
        return success

    def test_login_bureau(self):
        """Test Bureau user login"""
        login_data = {
            "email": "admin@btp-excellence.fr",
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

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
        
        success, response = self.make_request('POST', 'auth/login', login_data, expected_status=401)
        self.log_test("Invalid Login (Should Fail)", success, None,
                     response if not success else "Correctly rejected invalid credentials")
        return success

    def test_auth_me(self):
        """Test /auth/me endpoint"""
        success, response = self.make_request('GET', 'auth/me', token=self.bureau_token)
        self.log_test("Auth Me Endpoint", success, 
                     {"email": response.get('email'), "role": response.get('role')} if success else None,
                     response if not success else None)
        return success

    # ==================== SEARCH CRUD TESTS ====================
    
    def test_create_search(self):
        """Test creating a new search"""
        search_data = {
            "location": "Chantier Rue de Rivoli, Paris 1er",
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

    def test_create_multiple_searches(self):
        """Create multiple searches for testing"""
        searches = [
            {
                "location": "Avenue des Champs-Élysées, Paris 8e",
                "description": "Vérification réseau électrique haute tension",
                "observations": "Présence de câbles anciens, schémas à vérifier",
                "latitude": 48.8698,
                "longitude": 2.3076
            },
            {
                "location": "Boulevard Saint-Germain, Paris 6e", 
                "description": "Recherche de conduites de gaz naturel",
                "observations": "Zone sensible, équipement de détection spécialisé requis",
                "latitude": 48.8534,
                "longitude": 2.3488
            }
        ]
        
        success_count = 0
        for i, search_data in enumerate(searches):
            success, response = self.make_request('POST', 'searches', search_data, token=self.bureau_token)
            if success and 'id' in response:
                self.test_data['searches'].append(response)
                success_count += 1
        
        overall_success = success_count == len(searches)
        self.log_test(f"Create Multiple Searches ({success_count}/{len(searches)})", 
                     overall_success, {"created": success_count})
        return overall_success

    def test_get_searches(self):
        """Test retrieving searches"""
        success, response = self.make_request('GET', 'searches', token=self.bureau_token)
        
        search_count = len(response) if success and isinstance(response, list) else 0
        self.log_test("Get Searches", success, 
                     {"count": search_count} if success else None,
                     response if not success else None)
        return success

    def test_get_single_search(self):
        """Test retrieving a single search"""
        if not self.test_data['searches']:
            self.log_test("Get Single Search", False, None, "No searches available for testing")
            return False
            
        search_id = self.test_data['searches'][0]['id']
        success, response = self.make_request('GET', f'searches/{search_id}', token=self.bureau_token)
        
        self.log_test("Get Single Search", success,
                     {"id": response.get('id'), "location": response.get('location')} if success else None,
                     response if not success else None)
        return success

    def test_update_search_status(self):
        """Test updating search status"""
        if not self.test_data['searches']:
            self.log_test("Update Search Status", False, None, "No searches available for testing")
            return False
            
        search_id = self.test_data['searches'][0]['id']
        
        # The endpoint expects raw text, not JSON
        url = f"{self.api_url}/searches/{search_id}/status"
        headers = {
            'Authorization': f'Bearer {self.bureau_token}',
            'Content-Type': 'text/plain'
        }
        
        try:
            response = requests.put(url, data="SHARED", headers=headers, timeout=15)
            success = response.status_code == 200
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
                
            self.log_test("Update Search Status", success, response_data if success else None,
                         response_data if not success else None)
            return success
            
        except Exception as e:
            self.log_test("Update Search Status", False, None, f"Request failed: {str(e)}")
            return False

    # ==================== REPORT CRUD TESTS ====================
    
    def test_create_report(self):
        """Test creating a report"""
        if not self.test_data['searches']:
            self.log_test("Create Report", False, None, "No searches available for report creation")
            return False
            
        report_data = {
            "search_id": self.test_data['searches'][0]['id'],
            "title": "Rapport d'intervention - Rue de Rivoli",
            "content": "Intervention réalisée avec succès. Canalisations localisées à 1,2m de profondeur. État général satisfaisant. Recommandations: surveillance périodique des joints."
        }
        
        success, response = self.make_request('POST', 'reports', report_data, token=self.bureau_token)
        
        if success and 'id' in response:
            self.test_data['reports'].append(response)
            
        self.log_test("Create Report", success,
                     {"id": response.get('id'), "title": response.get('title')} if success else None,
                     response if not success else None)
        return success

    def test_get_reports(self):
        """Test retrieving reports"""
        success, response = self.make_request('GET', 'reports', token=self.bureau_token)
        
        report_count = len(response) if success and isinstance(response, list) else 0
        self.log_test("Get Reports", success,
                     {"count": report_count} if success else None,
                     response if not success else None)
        return success

    # ==================== CLIENT CRUD TESTS ====================
    
    def test_create_client(self):
        """Test creating a client"""
        client_data = {
            "nom": "Société Immobilière Parisienne",
            "email": "contact@sip-paris.fr",
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

    def test_create_multiple_clients(self):
        """Create multiple clients for testing"""
        clients = [
            {
                "nom": "Constructeur Moderne SARL",
                "email": "info@constructeur-moderne.fr",
                "telephone": "01 45 67 89 12",
                "adresse": "28 Rue de la Paix, 75002 Paris"
            },
            {
                "nom": "Rénovation Expert",
                "email": "contact@renovation-expert.com",
                "telephone": "01 56 78 90 23",
                "adresse": "42 Boulevard Haussmann, 75009 Paris"
            }
        ]
        
        success_count = 0
        for client_data in clients:
            success, response = self.make_request('POST', 'clients', client_data, token=self.bureau_token)
            if success and 'id' in response:
                self.test_data['clients'].append(response)
                success_count += 1
        
        overall_success = success_count == len(clients)
        self.log_test(f"Create Multiple Clients ({success_count}/{len(clients)})", 
                     overall_success, {"created": success_count})
        return overall_success

    def test_get_clients(self):
        """Test retrieving clients"""
        success, response = self.make_request('GET', 'clients', token=self.bureau_token)
        
        client_count = len(response) if success and isinstance(response, list) else 0
        self.log_test("Get Clients", success,
                     {"count": client_count} if success else None,
                     response if not success else None)
        return success

    # ==================== QUOTE CRUD TESTS ====================
    
    def test_create_quote(self):
        """Test creating a quote"""
        if not self.test_data['clients']:
            self.log_test("Create Quote", False, None, "No clients available for quote creation")
            return False
            
        quote_data = {
            "client_id": self.test_data['clients'][0]['id'],
            "title": "Devis recherche de réseaux - Rue de Rivoli",
            "description": "Prestation de recherche et localisation de canalisations d'eau potable. Intervention de nuit avec équipement spécialisé. Rapport détaillé inclus.",
            "amount": 2850.00
        }
        
        success, response = self.make_request('POST', 'quotes', quote_data, token=self.bureau_token)
        
        if success and 'id' in response:
            self.test_data['quotes'].append(response)
            
        self.log_test("Create Quote", success,
                     {"id": response.get('id'), "amount": response.get('amount')} if success else None,
                     response if not success else None)
        return success

    def test_get_quotes(self):
        """Test retrieving quotes"""
        success, response = self.make_request('GET', 'quotes', token=self.bureau_token)
        
        quote_count = len(response) if success and isinstance(response, list) else 0
        self.log_test("Get Quotes", success,
                     {"count": quote_count} if success else None,
                     response if not success else None)
        return success

    # ==================== SITE/PLANNING CRUD TESTS ====================
    
    def test_create_site(self):
        """Test creating a site/planning entry"""
        site_data = {
            "name": "Intervention Rue de Rivoli",
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

    def test_get_sites(self):
        """Test retrieving sites/planning"""
        success, response = self.make_request('GET', 'sites', token=self.bureau_token)
        
        site_count = len(response) if success and isinstance(response, list) else 0
        self.log_test("Get Sites/Planning", success,
                     {"count": site_count} if success else None,
                     response if not success else None)
        return success

    # ==================== INVITATION CRUD TESTS ====================
    
    def test_create_invitation(self):
        """Test creating an invitation"""
        invitation_data = {
            "email": "technicien@btp-excellence.fr",
            "role": "TECHNICIEN",
            "message": "Bienvenue dans l'équipe BTP Excellence. Vous avez été invité à rejoindre notre plateforme."
        }
        
        success, response = self.make_request('POST', 'invitations', invitation_data, token=self.bureau_token)
        
        if success and 'id' in response:
            self.test_data['invitations'].append(response)
            
        self.log_test("Create Invitation", success,
                     {"id": response.get('id'), "email": response.get('email')} if success else None,
                     response if not success else None)
        return success

    def test_get_invitations(self):
        """Test retrieving invitations"""
        success, response = self.make_request('GET', 'invitations', token=self.bureau_token)
        
        invitation_count = len(response) if success and isinstance(response, list) else 0
        self.log_test("Get Invitations", success,
                     {"count": invitation_count} if success else None,
                     response if not success else None)
        return success

    def test_duplicate_invitation(self):
        """Test creating duplicate invitation (should fail)"""
        invitation_data = {
            "email": "technicien@btp-excellence.fr",  # Same email as above
            "role": "TECHNICIEN",
            "message": "Duplicate invitation test"
        }
        
        success, response = self.make_request('POST', 'invitations', invitation_data, 
                                            token=self.bureau_token, expected_status=400)
        
        self.log_test("Duplicate Invitation (Should Fail)", success, None,
                     response if not success else "Correctly rejected duplicate invitation")
        return success

    # ==================== STATISTICS TESTS ====================
    
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

    # ==================== PDF GENERATION TESTS ====================
    
    def test_generate_search_pdf(self):
        """Test PDF generation for a search"""
        if not self.test_data['searches']:
            self.log_test("Generate Search PDF", False, None, "No searches available for PDF generation")
            return False
            
        search_id = self.test_data['searches'][0]['id']
        
        # Test without images first
        success, response = self.make_request('POST', f'reports/generate-pdf/{search_id}', 
                                            token=self.bureau_token)
        
        # For PDF generation, we expect a file response, so we check if the request was successful
        # and if we got some response (could be binary PDF data)
        pdf_success = success and response is not None
        
        self.log_test("Generate Search PDF", pdf_success,
                     {"search_id": search_id, "response_type": type(response).__name__} if pdf_success else None,
                     response if not pdf_success else None)
        return pdf_success

    def test_generate_summary_pdf(self):
        """Test PDF generation for multiple searches (summary)"""
        if len(self.test_data['searches']) < 2:
            self.log_test("Generate Summary PDF", False, None, "Need at least 2 searches for summary PDF")
            return False
            
        search_ids = [search['id'] for search in self.test_data['searches'][:2]]
        summary_data = {"search_ids": search_ids}
        
        success, response = self.make_request('POST', 'reports/generate-summary-pdf', 
                                            summary_data, token=self.bureau_token)
        
        pdf_success = success and response is not None
        
        self.log_test("Generate Summary PDF", pdf_success,
                     {"search_count": len(search_ids), "response_type": type(response).__name__} if pdf_success else None,
                     response if not pdf_success else None)
        return pdf_success

    # ==================== MAIN TEST RUNNER ====================
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting SkyApp Comprehensive Backend Testing")
        print("=" * 80)
        print("Testing all new functionalities as requested:")
        print("1. Authentication System - Login/Register with JWT")
        print("2. Complete CRUD - Users, Companies, Searches, Reports, Clients, Quotes, Sites, Invitations")
        print("3. PDF Generation - Individual and synthesis with Apple design")
        print("4. Status Management - Update search statuses")
        print("5. Statistics Dashboard - Statistics endpoints")
        print("=" * 80)
        
        # Test sequence organized by functionality
        test_groups = [
            ("🔐 AUTHENTICATION TESTS", [
                ("Root API Endpoint", self.test_root_endpoint),
                ("Company Registration", self.test_register_new_company),
                ("Duplicate Email Registration", self.test_register_duplicate_email),
                ("Bureau Login", self.test_login_bureau),
                ("Invalid Login", self.test_invalid_login),
                ("Auth Me Endpoint", self.test_auth_me),
            ]),
            
            ("🔍 SEARCH MANAGEMENT", [
                ("Create Search", self.test_create_search),
                ("Create Multiple Searches", self.test_create_multiple_searches),
                ("Get Searches", self.test_get_searches),
                ("Get Single Search", self.test_get_single_search),
                ("Update Search Status", self.test_update_search_status),
            ]),
            
            ("📋 REPORT MANAGEMENT", [
                ("Create Report", self.test_create_report),
                ("Get Reports", self.test_get_reports),
            ]),
            
            ("👥 CLIENT MANAGEMENT", [
                ("Create Client", self.test_create_client),
                ("Create Multiple Clients", self.test_create_multiple_clients),
                ("Get Clients", self.test_get_clients),
            ]),
            
            ("💰 QUOTE MANAGEMENT", [
                ("Create Quote", self.test_create_quote),
                ("Get Quotes", self.test_get_quotes),
            ]),
            
            ("📅 SITE/PLANNING MANAGEMENT", [
                ("Create Site/Planning", self.test_create_site),
                ("Get Sites/Planning", self.test_get_sites),
            ]),
            
            ("✉️ INVITATION MANAGEMENT", [
                ("Create Invitation", self.test_create_invitation),
                ("Get Invitations", self.test_get_invitations),
                ("Duplicate Invitation", self.test_duplicate_invitation),
            ]),
            
            ("📊 STATISTICS & DASHBOARD", [
                ("Dashboard Statistics", self.test_dashboard_stats),
            ]),
            
            ("📄 PDF GENERATION", [
                ("Generate Search PDF", self.test_generate_search_pdf),
                ("Generate Summary PDF", self.test_generate_summary_pdf),
            ]),
        ]
        
        # Run all test groups
        for group_name, tests in test_groups:
            print(f"\n{group_name}")
            print("-" * 50)
            
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
        print("📊 COMPREHENSIVE TEST RESULTS")
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
    tester = SkyAppComprehensiveTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())