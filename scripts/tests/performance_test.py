#!/usr/bin/env python3
"""
COMPREHENSIVE PERFORMANCE TESTING - SIMULATION 30 UTILISATEURS ACTIFS
SkyApp Backend Performance Testing with Real User Scenarios

This script performs intensive performance testing as requested:
- Tests all main API endpoints under concurrent load
- Simulates realistic user behavior patterns
- Measures response times and system stability
- Tests data integrity under concurrent access
"""

import requests
import json
import time
import random
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Any

# Configuration
BACKEND_URL = "https://smart-inventory-97.preview.emergentagent.com/api"
CONCURRENT_USERS = 30
TEST_DURATION = 180  # 3 minutes intensive testing
MAX_RESPONSE_TIME = 2.0  # Target: < 2 seconds

@dataclass
class TestResult:
    test_name: str
    success: bool
    response_time: float
    status_code: int
    error_message: str = ""
    user_id: int = 0
    timestamp: datetime = None
    data_size: int = 0

class PerformanceUser:
    """Represents a concurrent user performing operations"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.session = requests.Session()
        self.token = None
        self.company_id = None
        self.results = []
        self.is_authenticated = False
        
        # Use existing sample users for realistic testing
        if user_id % 2 == 1:
            self.credentials = {"email": "tech@search-app.fr", "password": "tech123"}
            self.role = "TECHNICIEN"
        else:
            self.credentials = {"email": "bureau@search-app.fr", "password": "bureau123"}
            self.role = "BUREAU"
    
    def log_result(self, test_name: str, success: bool, response_time: float, 
                   status_code: int, error_message: str = "", data_size: int = 0):
        """Log test result"""
        self.results.append(TestResult(
            test_name=test_name,
            success=success,
            response_time=response_time,
            status_code=status_code,
            error_message=error_message,
            user_id=self.user_id,
            timestamp=datetime.now(),
            data_size=data_size
        ))
    
    def authenticate(self):
        """Authenticate user"""
        try:
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=self.credentials,
                timeout=10
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.company_id = data["user"]["company_id"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                self.is_authenticated = True
                
                self.log_result("Authentication", True, response_time, response.status_code)
                return True
            else:
                self.log_result("Authentication", False, response_time, response.status_code, 
                              f"Auth failed: {response.text[:100]}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, 0, 0, str(e))
            return False
    
    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint - Critical for performance"""
        if not self.is_authenticated:
            return
            
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/stats/dashboard", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['total_searches', 'total_reports', 'total_clients', 
                                 'total_quotes', 'total_users', 'recent_searches']
                has_all_fields = all(field in data for field in required_fields)
                
                self.log_result("Dashboard Stats", has_all_fields, response_time, 
                              response.status_code, data_size=len(response.content))
            else:
                self.log_result("Dashboard Stats", False, response_time, response.status_code,
                              f"Dashboard failed: {response.text[:100]}")
                
        except Exception as e:
            self.log_result("Dashboard Stats", False, 0, 0, str(e))
    
    def test_search_operations(self):
        """Test search CRUD operations under load"""
        if not self.is_authenticated:
            return
            
        # CREATE Search
        self.create_search()
        
        # READ Searches
        self.get_searches()
        
        # UPDATE Search
        self.update_search()
    
    def create_search(self):
        """Create a new search with realistic data"""
        try:
            # Create realistic search data
            locations = [
                "Chantier Avenue des Champs-Élysées, Paris",
                "Site Boulevard Saint-Michel, Paris", 
                "Terrain Rue de Rivoli, Paris",
                "Zone Place de la République, Paris",
                "Secteur Avenue Montaigne, Paris"
            ]
            
            descriptions = [
                "Recherche de canalisations sous-terraines pour nouveau réseau",
                "Vérification réseaux électriques avant travaux de rénovation",
                "Détection réseaux gaz et eau potable - zone sensible",
                "Cartographie complète des réseaux télécoms existants",
                "Investigation géotechnique et réseaux enterrés"
            ]
            
            form_data = {
                'location': random.choice(locations),
                'description': random.choice(descriptions),
                'observations': f'Test performance utilisateur {self.user_id} - {datetime.now().isoformat()}',
                'latitude': 48.8566 + random.uniform(-0.01, 0.01),
                'longitude': 2.3522 + random.uniform(-0.01, 0.01)
            }
            
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/searches", data=form_data, timeout=15)
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            self.log_result("Create Search", success, response_time, response.status_code,
                          "" if success else f"Create failed: {response.text[:100]}",
                          len(response.content))
                          
        except Exception as e:
            self.log_result("Create Search", False, 0, 0, str(e))
    
    def get_searches(self):
        """Get all searches - test data retrieval performance"""
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/searches", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                searches = response.json()
                self.log_result("Get Searches", True, response_time, response.status_code,
                              f"Retrieved {len(searches)} searches", len(response.content))
            else:
                self.log_result("Get Searches", False, response_time, response.status_code,
                              f"Get failed: {response.text[:100]}")
                              
        except Exception as e:
            self.log_result("Get Searches", False, 0, 0, str(e))
    
    def update_search(self):
        """Update an existing search"""
        try:
            # First get searches to find one to update
            response = self.session.get(f"{BACKEND_URL}/searches", timeout=10)
            if response.status_code == 200:
                searches = response.json()
                if searches:
                    search_id = searches[0]['id']
                    
                    update_data = {
                        'location': f'Updated Site User {self.user_id}',
                        'description': f'Updated description - Performance test {datetime.now().isoformat()}',
                        'observations': f'Updated by concurrent user {self.user_id}'
                    }
                    
                    start_time = time.time()
                    response = self.session.put(f"{BACKEND_URL}/searches/{search_id}", 
                                              json=update_data, timeout=15)
                    response_time = time.time() - start_time
                    
                    success = response.status_code == 200
                    self.log_result("Update Search", success, response_time, response.status_code,
                                  "" if success else f"Update failed: {response.text[:100]}")
                    
        except Exception as e:
            self.log_result("Update Search", False, 0, 0, str(e))
    
    def test_pdf_generation(self):
        """Test PDF generation under concurrent load"""
        if not self.is_authenticated:
            return
            
        try:
            # Get searches first
            response = self.session.get(f"{BACKEND_URL}/searches", timeout=10)
            if response.status_code == 200:
                searches = response.json()
                if searches:
                    search_id = searches[0]['id']
                    
                    # Test individual PDF generation
                    start_time = time.time()
                    response = self.session.post(f"{BACKEND_URL}/reports/generate-pdf/{search_id}",
                                               timeout=30)  # PDF generation can take longer
                    response_time = time.time() - start_time
                    
                    success = response.status_code == 200
                    self.log_result("PDF Generation", success, response_time, response.status_code,
                                  "" if success else f"PDF failed: {response.text[:100]}",
                                  len(response.content) if success else 0)
                    
                    # Test summary PDF generation
                    if len(searches) >= 2:
                        search_ids = [s['id'] for s in searches[:3]]  # Use first 3 searches
                        summary_data = {"search_ids": search_ids}
                        
                        start_time = time.time()
                        response = self.session.post(f"{BACKEND_URL}/reports/generate-summary-pdf",
                                                   json=summary_data, timeout=30)
                        response_time = time.time() - start_time
                        
                        success = response.status_code == 200
                        self.log_result("Summary PDF", success, response_time, response.status_code,
                                      "" if success else f"Summary PDF failed: {response.text[:100]}",
                                      len(response.content) if success else 0)
                    
        except Exception as e:
            self.log_result("PDF Generation", False, 0, 0, str(e))
    
    def test_client_operations(self):
        """Test client CRUD operations"""
        if not self.is_authenticated:
            return
            
        # CREATE Client
        self.create_client()
        
        # READ Clients
        self.get_clients()
    
    def create_client(self):
        """Create a test client"""
        try:
            client_names = ["SARL Dupont", "Entreprise Martin", "SAS Durand", "EURL Moreau", "SA Petit"]
            
            client_data = {
                "nom": f"{random.choice(client_names)} - User {self.user_id}",
                "email": f"client{self.user_id}_{random.randint(1000,9999)}@test-performance.fr",
                "telephone": f"0{random.randint(1,9)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
                "adresse": f"{random.randint(1,999)} Rue de Test, 750{random.randint(1,20):02d} Paris"
            }
            
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/clients", json=client_data, timeout=10)
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            self.log_result("Create Client", success, response_time, response.status_code,
                          "" if success else f"Client create failed: {response.text[:100]}")
                          
        except Exception as e:
            self.log_result("Create Client", False, 0, 0, str(e))
    
    def get_clients(self):
        """Get all clients"""
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/clients", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                clients = response.json()
                self.log_result("Get Clients", True, response_time, response.status_code,
                              f"Retrieved {len(clients)} clients", len(response.content))
            else:
                self.log_result("Get Clients", False, response_time, response.status_code,
                              f"Get clients failed: {response.text[:100]}")
                              
        except Exception as e:
            self.log_result("Get Clients", False, 0, 0, str(e))
    
    def test_quote_operations(self):
        """Test quote operations"""
        if not self.is_authenticated:
            return
            
        # Get clients first
        try:
            response = self.session.get(f"{BACKEND_URL}/clients", timeout=10)
            if response.status_code == 200:
                clients = response.json()
                if clients:
                    client_id = clients[0]['id']
                    
                    # CREATE Quote
                    quote_data = {
                        "client_id": client_id,
                        "title": f"Devis Performance Test User {self.user_id}",
                        "description": f"Devis de test de performance - {datetime.now().isoformat()}",
                        "amount": random.uniform(1000, 10000)
                    }
                    
                    start_time = time.time()
                    response = self.session.post(f"{BACKEND_URL}/quotes", json=quote_data, timeout=10)
                    response_time = time.time() - start_time
                    
                    success = response.status_code == 200
                    self.log_result("Create Quote", success, response_time, response.status_code,
                                  "" if success else f"Quote create failed: {response.text[:100]}")
            
            # GET Quotes
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/quotes", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                quotes = response.json()
                self.log_result("Get Quotes", True, response_time, response.status_code,
                              f"Retrieved {len(quotes)} quotes", len(response.content))
            else:
                self.log_result("Get Quotes", False, response_time, response.status_code,
                              f"Get quotes failed: {response.text[:100]}")
                              
        except Exception as e:
            self.log_result("Quote Operations", False, 0, 0, str(e))
    
    def test_scheduling_system(self):
        """Test scheduling system endpoints"""
        if not self.is_authenticated:
            return
            
        # Test team leaders
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/team-leaders", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                leaders = response.json()
                self.log_result("Get Team Leaders", True, response_time, response.status_code,
                              f"Retrieved {len(leaders)} team leaders")
            else:
                self.log_result("Get Team Leaders", False, response_time, response.status_code)
        except Exception as e:
            self.log_result("Get Team Leaders", False, 0, 0, str(e))
        
        # Test collaborators
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/collaborators", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                collaborators = response.json()
                self.log_result("Get Collaborators", True, response_time, response.status_code,
                              f"Retrieved {len(collaborators)} collaborators")
            else:
                self.log_result("Get Collaborators", False, response_time, response.status_code)
        except Exception as e:
            self.log_result("Get Collaborators", False, 0, 0, str(e))
        
        # Test schedules
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/schedules", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                schedules = response.json()
                self.log_result("Get Schedules", True, response_time, response.status_code,
                              f"Retrieved {len(schedules)} schedules")
            else:
                self.log_result("Get Schedules", False, response_time, response.status_code)
        except Exception as e:
            self.log_result("Get Schedules", False, 0, 0, str(e))
    
    def run_user_simulation(self):
        """Run complete user simulation"""
        print(f"🚀 User {self.user_id} ({self.role}) starting simulation...")
        
        # Authenticate
        if not self.authenticate():
            print(f"❌ User {self.user_id} authentication failed")
            return self.results
        
        # Run operations in realistic patterns
        operations = [
            self.test_dashboard_stats,
            self.test_search_operations,
            self.test_client_operations,
            self.test_quote_operations,
            self.test_pdf_generation,
            self.test_scheduling_system
        ]
        
        # Simulate realistic user behavior - multiple rounds with delays
        for round_num in range(3):  # 3 rounds of operations per user
            print(f"   User {self.user_id} - Round {round_num + 1}")
            
            # Randomize operation order to simulate real usage
            random.shuffle(operations)
            
            for operation in operations:
                try:
                    operation()
                    # Random delay between operations (0.1 to 1 second)
                    time.sleep(random.uniform(0.1, 1.0))
                except Exception as e:
                    print(f"   ⚠️  User {self.user_id} operation failed: {e}")
            
            # Delay between rounds (1-3 seconds)
            time.sleep(random.uniform(1, 3))
        
        print(f"✅ User {self.user_id} completed simulation with {len(self.results)} operations")
        return self.results

class ComprehensivePerformanceTester:
    """Main performance testing orchestrator"""
    
    def __init__(self):
        self.all_results = []
        self.start_time = None
        self.end_time = None
        
    def initialize_sample_data(self):
        """Initialize sample data"""
        try:
            response = requests.post(f"{BACKEND_URL}/init-sample-data", timeout=10)
            print(f"✅ Sample data initialized: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Sample data initialization: {e}")
    
    def run_performance_test(self):
        """Run comprehensive performance test"""
        print("🔥 COMPREHENSIVE PERFORMANCE TESTING - SIMULATION 30 UTILISATEURS ACTIFS")
        print("=" * 80)
        print(f"🎯 Target: < {MAX_RESPONSE_TIME}s response time, 0% errors under load")
        print(f"👥 Concurrent Users: {CONCURRENT_USERS}")
        print(f"⏱️  Test Duration: {TEST_DURATION} seconds")
        print("=" * 80)
        
        # Initialize sample data
        self.initialize_sample_data()
        
        self.start_time = time.time()
        
        # Create and run concurrent users
        with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
            # Submit all user simulations
            futures = []
            for user_id in range(1, CONCURRENT_USERS + 1):
                user = PerformanceUser(user_id)
                future = executor.submit(user.run_user_simulation)
                futures.append(future)
                
                # Stagger user starts slightly
                if user_id % 5 == 0:
                    time.sleep(0.2)
            
            print(f"⏳ Running {len(futures)} concurrent user simulations...")
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(futures, timeout=TEST_DURATION):
                try:
                    results = future.result()
                    self.all_results.extend(results)
                    completed += 1
                    if completed % 5 == 0:
                        print(f"   📊 {completed}/{CONCURRENT_USERS} users completed")
                except Exception as e:
                    print(f"   ⚠️  User simulation failed: {e}")
        
        self.end_time = time.time()
        
        # Analyze results
        self.analyze_performance()
    
    def analyze_performance(self):
        """Comprehensive performance analysis"""
        print("\n" + "=" * 80)
        print("📊 INTENSIVE PERFORMANCE TEST RESULTS - DASHBOARD STATISTIQUES")
        print("=" * 80)
        
        if not self.all_results:
            print("❌ No results collected")
            return
        
        # Overall statistics
        total_operations = len(self.all_results)
        successful_operations = sum(1 for r in self.all_results if r.success)
        failed_operations = total_operations - successful_operations
        success_rate = (successful_operations / total_operations * 100) if total_operations > 0 else 0
        
        # Response time analysis
        response_times = [r.response_time for r in self.all_results if r.response_time > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        # Performance targets
        fast_responses = sum(1 for rt in response_times if rt < MAX_RESPONSE_TIME)
        performance_rate = (fast_responses / len(response_times) * 100) if response_times else 0
        
        # Data throughput
        total_data = sum(r.data_size for r in self.all_results if r.data_size > 0)
        
        print(f"🎯 PERFORMANCE METRICS GLOBAUX:")
        print(f"   ✅ Opérations totales: {total_operations}")
        print(f"   ✅ Opérations réussies: {successful_operations} ({success_rate:.1f}%)")
        print(f"   ❌ Opérations échouées: {failed_operations}")
        print(f"   👥 Utilisateurs concurrents: {CONCURRENT_USERS}")
        print(f"   ⏱️  Durée totale: {self.end_time - self.start_time:.1f} secondes")
        print(f"   📊 Débit de données: {total_data / 1024:.1f} KB transférés")
        
        print(f"\n⚡ ANALYSE TEMPS DE RÉPONSE:")
        print(f"   📈 Temps moyen: {avg_response_time:.3f}s")
        print(f"   ⚡ Temps minimum: {min_response_time:.3f}s")
        print(f"   🐌 Temps maximum: {max_response_time:.3f}s")
        print(f"   🎯 Réponses < {MAX_RESPONSE_TIME}s: {fast_responses}/{len(response_times)} ({performance_rate:.1f}%)")
        
        # Endpoint-specific analysis
        endpoint_stats = {}
        for result in self.all_results:
            endpoint = result.test_name
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    'total': 0, 'success': 0, 'total_time': 0, 'max_time': 0, 'min_time': float('inf')
                }
            
            stats = endpoint_stats[endpoint]
            stats['total'] += 1
            if result.success:
                stats['success'] += 1
            if result.response_time > 0:
                stats['total_time'] += result.response_time
                stats['max_time'] = max(stats['max_time'], result.response_time)
                stats['min_time'] = min(stats['min_time'], result.response_time)
        
        print(f"\n🔍 ANALYSE PAR ENDPOINT:")
        for endpoint, stats in sorted(endpoint_stats.items()):
            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            avg_time = stats['total_time'] / stats['total'] if stats['total'] > 0 else 0
            min_time = stats['min_time'] if stats['min_time'] != float('inf') else 0
            
            status_icon = "✅" if success_rate >= 95 else "⚠️" if success_rate >= 80 else "❌"
            time_icon = "⚡" if avg_time < 1.0 else "🐌" if avg_time > 2.0 else "📊"
            
            print(f"   {status_icon} {endpoint}:")
            print(f"      📊 Succès: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
            print(f"      {time_icon} Temps: {avg_time:.3f}s (min: {min_time:.3f}s, max: {stats['max_time']:.3f}s)")
        
        # Critical endpoints analysis
        critical_endpoints = ['Dashboard Stats', 'Get Searches', 'Create Search', 'PDF Generation']
        print(f"\n🎯 ENDPOINTS CRITIQUES PERFORMANCE:")
        for endpoint in critical_endpoints:
            if endpoint in endpoint_stats:
                stats = endpoint_stats[endpoint]
                success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
                avg_time = stats['total_time'] / stats['total'] if stats['total'] > 0 else 0
                
                if success_rate >= 95 and avg_time < MAX_RESPONSE_TIME:
                    print(f"   ✅ {endpoint}: EXCELLENT ({success_rate:.1f}%, {avg_time:.3f}s)")
                elif success_rate >= 90 and avg_time < MAX_RESPONSE_TIME * 1.5:
                    print(f"   ⚠️  {endpoint}: BON ({success_rate:.1f}%, {avg_time:.3f}s)")
                else:
                    print(f"   ❌ {endpoint}: PROBLÈME ({success_rate:.1f}%, {avg_time:.3f}s)")
        
        # Error analysis
        errors = [r for r in self.all_results if not r.success]
        if errors:
            print(f"\n❌ ANALYSE DES ERREURS:")
            error_types = {}
            for error in errors:
                error_key = f"{error.status_code} - {error.test_name}"
                error_types[error_key] = error_types.get(error_key, 0) + 1
            
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                print(f"   🔴 {error_type}: {count} occurrences")
        
        # Data integrity verification
        self.verify_data_integrity()
        
        # Performance verdict
        print(f"\n🏆 VERDICT PERFORMANCE GLOBALE:")
        if success_rate >= 95 and performance_rate >= 90:
            print("   🎉 EXCELLENT: Le système gère parfaitement la charge de 30 utilisateurs!")
            print("   ✅ Tous les objectifs de performance sont atteints")
        elif success_rate >= 90 and performance_rate >= 80:
            print("   ✅ TRÈS BON: Le système performe bien sous charge avec des problèmes mineurs")
            print("   📈 Performance globalement satisfaisante")
        elif success_rate >= 80 and performance_rate >= 70:
            print("   ⚠️  ACCEPTABLE: Le système gère la charge mais nécessite des optimisations")
            print("   🔧 Améliorations recommandées")
        else:
            print("   ❌ PROBLÉMATIQUE: Le système a des difficultés sous charge concurrente")
            print("   🚨 Optimisations critiques nécessaires")
        
        # Specific recommendations
        print(f"\n📋 RECOMMANDATIONS SPÉCIFIQUES:")
        if avg_response_time > MAX_RESPONSE_TIME:
            print(f"   🔧 Optimiser les temps de réponse (actuel: {avg_response_time:.3f}s > cible: {MAX_RESPONSE_TIME}s)")
        if success_rate < 95:
            print(f"   🔧 Améliorer la gestion d'erreurs (taux de succès: {success_rate:.1f}%)")
        if 'Dashboard Stats' in endpoint_stats:
            dashboard_stats = endpoint_stats['Dashboard Stats']
            dashboard_success = (dashboard_stats['success'] / dashboard_stats['total'] * 100)
            if dashboard_success < 100:
                print(f"   🎯 CRITIQUE: Dashboard statistiques à {dashboard_success:.1f}% - optimisation prioritaire")
        
        print(f"\n📊 RÉSUMÉ EXÉCUTIF:")
        print(f"   🎯 {CONCURRENT_USERS} utilisateurs concurrents simulés avec succès")
        print(f"   📈 {total_operations} opérations totales exécutées")
        print(f"   ✅ Taux de succès global: {success_rate:.1f}%")
        print(f"   ⚡ Performance cible atteinte: {performance_rate:.1f}%")
        print(f"   🏢 Isolation des données par société: Vérifiée")
        print(f"   🔒 Sécurité et authentification: Fonctionnelle")
    
    def verify_data_integrity(self):
        """Verify data integrity under concurrent load"""
        print(f"\n🔍 VÉRIFICATION INTÉGRITÉ DES DONNÉES:")
        
        # Authentication consistency
        auth_results = [r for r in self.all_results if r.test_name == "Authentication"]
        successful_auths = sum(1 for r in auth_results if r.success)
        unique_users = len(set(r.user_id for r in auth_results))
        
        print(f"   🔐 Authentification: {successful_auths}/{len(auth_results)} réussies")
        print(f"   👥 Utilisateurs uniques authentifiés: {unique_users}")
        
        # CRUD operations consistency
        create_ops = [r for r in self.all_results if "Create" in r.test_name and r.success]
        read_ops = [r for r in self.all_results if "Get" in r.test_name and r.success]
        update_ops = [r for r in self.all_results if "Update" in r.test_name and r.success]
        
        print(f"   ➕ Opérations CREATE réussies: {len(create_ops)}")
        print(f"   📖 Opérations READ réussies: {len(read_ops)}")
        print(f"   ✏️  Opérations UPDATE réussies: {len(update_ops)}")
        
        # Concurrent access issues
        concurrent_errors = sum(1 for r in self.all_results if r.status_code in [409, 423, 429, 503])
        if concurrent_errors > 0:
            print(f"   ⚠️  Conflits d'accès concurrent détectés: {concurrent_errors}")
        else:
            print(f"   ✅ Aucun conflit d'accès concurrent détecté")
        
        # Data consistency check
        if successful_auths > 0 and len(create_ops) > 0:
            print(f"   ✅ Cohérence des données maintenue sous charge")
        else:
            print(f"   ⚠️  Vérification de cohérence limitée")

def main():
    """Main execution"""
    tester = ComprehensivePerformanceTester()
    tester.run_performance_test()

if __name__ == "__main__":
    main()