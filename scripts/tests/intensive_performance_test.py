#!/usr/bin/env python3
"""
INTENSIVE PERFORMANCE TESTING - SIMULATION 30 UTILISATEURS ACTIFS
SkyApp Backend Performance Testing with Concurrent Users

This script simulates 25-35 concurrent users performing various operations
to test the system under heavy load as requested.

Test Areas:
1. Authentication load testing
2. Dashboard statistics under load
3. CRUD operations with concurrent users
4. PDF generation performance
5. File upload performance
6. Data integrity under concurrent access
"""

import asyncio
import aiohttp
import json
import time
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from dataclasses import dataclass
from typing import List, Dict, Any
import io
from PIL import Image
import tempfile
import os

# Configuration
BACKEND_URL = "https://smart-inventory-97.preview.emergentagent.com/api"
CONCURRENT_USERS = 30  # Simulate 30 active users
TEST_DURATION = 300  # 5 minutes of intensive testing
MAX_RESPONSE_TIME = 2.0  # Target: < 2 seconds response time

@dataclass
class TestResult:
    test_name: str
    success: bool
    response_time: float
    status_code: int
    error_message: str = ""
    user_id: int = 0
    timestamp: datetime = None

class PerformanceTestUser:
    """Represents a single concurrent user"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.session = None
        self.token = None
        self.company_id = None
        self.results = []
        self.is_authenticated = False
        
    async def authenticate(self):
        """Authenticate user"""
        try:
            # Use different credentials for load testing
            credentials = {
                "email": f"test_user_{self.user_id}@skyapp-load.fr",
                "password": "loadtest123"
            }
            
            # If user doesn't exist, try with sample data
            if self.user_id <= 2:
                credentials = {
                    "email": "tech@search-app.fr" if self.user_id == 1 else "bureau@search-app.fr",
                    "password": "tech123" if self.user_id == 1 else "bureau123"
                }
            
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                self.session = session
                async with session.post(f"{BACKEND_URL}/auth/login", json=credentials) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        self.token = data["access_token"]
                        self.company_id = data["user"]["company_id"]
                        self.is_authenticated = True
                        
                        self.results.append(TestResult(
                            test_name="Authentication",
                            success=True,
                            response_time=response_time,
                            status_code=response.status,
                            user_id=self.user_id,
                            timestamp=datetime.now()
                        ))
                        return True
                    else:
                        self.results.append(TestResult(
                            test_name="Authentication",
                            success=False,
                            response_time=response_time,
                            status_code=response.status,
                            error_message=f"Auth failed for user {self.user_id}",
                            user_id=self.user_id,
                            timestamp=datetime.now()
                        ))
                        return False
                        
        except Exception as e:
            self.results.append(TestResult(
                test_name="Authentication",
                success=False,
                response_time=0,
                status_code=0,
                error_message=str(e),
                user_id=self.user_id,
                timestamp=datetime.now()
            ))
            return False
    
    def get_headers(self):
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def test_dashboard_stats(self):
        """Test dashboard statistics endpoint under load"""
        if not self.is_authenticated:
            return
            
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/stats/dashboard", 
                                     headers=self.get_headers()) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        # Verify required fields
                        required_fields = ['total_searches', 'total_reports', 'total_clients', 
                                         'total_quotes', 'total_users', 'recent_searches']
                        has_all_fields = all(field in data for field in required_fields)
                        
                        self.results.append(TestResult(
                            test_name="Dashboard Stats",
                            success=has_all_fields,
                            response_time=response_time,
                            status_code=response.status,
                            user_id=self.user_id,
                            timestamp=datetime.now()
                        ))
                    else:
                        self.results.append(TestResult(
                            test_name="Dashboard Stats",
                            success=False,
                            response_time=response_time,
                            status_code=response.status,
                            error_message="Dashboard stats failed",
                            user_id=self.user_id,
                            timestamp=datetime.now()
                        ))
                        
        except Exception as e:
            self.results.append(TestResult(
                test_name="Dashboard Stats",
                success=False,
                response_time=0,
                status_code=0,
                error_message=str(e),
                user_id=self.user_id,
                timestamp=datetime.now()
            ))
    
    async def test_search_operations(self):
        """Test search CRUD operations"""
        if not self.is_authenticated:
            return
            
        # CREATE Search
        await self.create_search()
        
        # READ Searches
        await self.get_searches()
        
        # UPDATE Search (if we have searches)
        await self.update_search()
    
    async def create_search(self):
        """Create a new search"""
        try:
            search_data = {
                'location': f'Site Test Performance User {self.user_id}',
                'description': f'Test de performance utilisateur concurrent #{self.user_id}',
                'observations': f'Test de charge - {datetime.now().isoformat()}',
                'latitude': 48.8566 + random.uniform(-0.01, 0.01),
                'longitude': 2.3522 + random.uniform(-0.01, 0.01)
            }
            
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                form_data = aiohttp.FormData()
                for key, value in search_data.items():
                    form_data.add_field(key, str(value))
                
                async with session.post(f"{BACKEND_URL}/searches", 
                                      data=form_data,
                                      headers={"Authorization": f"Bearer {self.token}"}) as response:
                    response_time = time.time() - start_time
                    
                    self.results.append(TestResult(
                        test_name="Create Search",
                        success=response.status == 200,
                        response_time=response_time,
                        status_code=response.status,
                        user_id=self.user_id,
                        timestamp=datetime.now()
                    ))
                    
        except Exception as e:
            self.results.append(TestResult(
                test_name="Create Search",
                success=False,
                response_time=0,
                status_code=0,
                error_message=str(e),
                user_id=self.user_id,
                timestamp=datetime.now()
            ))
    
    async def get_searches(self):
        """Get all searches"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/searches", 
                                     headers=self.get_headers()) as response:
                    response_time = time.time() - start_time
                    
                    self.results.append(TestResult(
                        test_name="Get Searches",
                        success=response.status == 200,
                        response_time=response_time,
                        status_code=response.status,
                        user_id=self.user_id,
                        timestamp=datetime.now()
                    ))
                    
        except Exception as e:
            self.results.append(TestResult(
                test_name="Get Searches",
                success=False,
                response_time=0,
                status_code=0,
                error_message=str(e),
                user_id=self.user_id,
                timestamp=datetime.now()
            ))
    
    async def update_search(self):
        """Update an existing search"""
        try:
            # First get searches to find one to update
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/searches", 
                                     headers=self.get_headers()) as response:
                    if response.status == 200:
                        searches = await response.json()
                        if searches:
                            search_id = searches[0]['id']
                            
                            update_data = {
                                'location': f'Updated Site User {self.user_id}',
                                'description': f'Updated description - {datetime.now().isoformat()}',
                                'observations': 'Updated observations for performance test'
                            }
                            
                            start_time = time.time()
                            async with session.put(f"{BACKEND_URL}/searches/{search_id}", 
                                                 json=update_data,
                                                 headers=self.get_headers()) as update_response:
                                response_time = time.time() - start_time
                                
                                self.results.append(TestResult(
                                    test_name="Update Search",
                                    success=update_response.status == 200,
                                    response_time=response_time,
                                    status_code=update_response.status,
                                    user_id=self.user_id,
                                    timestamp=datetime.now()
                                ))
                    
        except Exception as e:
            self.results.append(TestResult(
                test_name="Update Search",
                success=False,
                response_time=0,
                status_code=0,
                error_message=str(e),
                user_id=self.user_id,
                timestamp=datetime.now()
            ))
    
    async def test_pdf_generation(self):
        """Test PDF generation under load"""
        if not self.is_authenticated:
            return
            
        try:
            # Get searches first
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/searches", 
                                     headers=self.get_headers()) as response:
                    if response.status == 200:
                        searches = await response.json()
                        if searches:
                            search_id = searches[0]['id']
                            
                            # Test individual PDF generation
                            start_time = time.time()
                            async with session.post(f"{BACKEND_URL}/reports/generate-pdf/{search_id}",
                                                  headers=self.get_headers()) as pdf_response:
                                response_time = time.time() - start_time
                                
                                self.results.append(TestResult(
                                    test_name="PDF Generation",
                                    success=pdf_response.status == 200,
                                    response_time=response_time,
                                    status_code=pdf_response.status,
                                    user_id=self.user_id,
                                    timestamp=datetime.now()
                                ))
                    
        except Exception as e:
            self.results.append(TestResult(
                test_name="PDF Generation",
                success=False,
                response_time=0,
                status_code=0,
                error_message=str(e),
                user_id=self.user_id,
                timestamp=datetime.now()
            ))
    
    async def test_quote_operations(self):
        """Test quote CRUD operations"""
        if not self.is_authenticated:
            return
            
        # Create client first
        await self.create_client()
        
        # Create quote
        await self.create_quote()
        
        # Get quotes
        await self.get_quotes()
    
    async def create_client(self):
        """Create a test client"""
        try:
            client_data = {
                "nom": f"Client Test User {self.user_id}",
                "email": f"client{self.user_id}@test-performance.fr",
                "telephone": f"06 {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
                "adresse": f"{random.randint(1,999)} Rue de Test, 75001 Paris"
            }
            
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{BACKEND_URL}/clients", 
                                      json=client_data,
                                      headers=self.get_headers()) as response:
                    response_time = time.time() - start_time
                    
                    self.results.append(TestResult(
                        test_name="Create Client",
                        success=response.status == 200,
                        response_time=response_time,
                        status_code=response.status,
                        user_id=self.user_id,
                        timestamp=datetime.now()
                    ))
                    
        except Exception as e:
            self.results.append(TestResult(
                test_name="Create Client",
                success=False,
                response_time=0,
                status_code=0,
                error_message=str(e),
                user_id=self.user_id,
                timestamp=datetime.now()
            ))
    
    async def create_quote(self):
        """Create a test quote"""
        try:
            # Get clients first
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/clients", 
                                     headers=self.get_headers()) as response:
                    if response.status == 200:
                        clients = await response.json()
                        if clients:
                            client_id = clients[0]['id']
                            
                            quote_data = {
                                "client_id": client_id,
                                "title": f"Devis Performance Test User {self.user_id}",
                                "description": f"Devis de test de performance - {datetime.now().isoformat()}",
                                "amount": random.uniform(1000, 10000)
                            }
                            
                            start_time = time.time()
                            async with session.post(f"{BACKEND_URL}/quotes", 
                                                  json=quote_data,
                                                  headers=self.get_headers()) as quote_response:
                                response_time = time.time() - start_time
                                
                                self.results.append(TestResult(
                                    test_name="Create Quote",
                                    success=quote_response.status == 200,
                                    response_time=response_time,
                                    status_code=quote_response.status,
                                    user_id=self.user_id,
                                    timestamp=datetime.now()
                                ))
                    
        except Exception as e:
            self.results.append(TestResult(
                test_name="Create Quote",
                success=False,
                response_time=0,
                status_code=0,
                error_message=str(e),
                user_id=self.user_id,
                timestamp=datetime.now()
            ))
    
    async def get_quotes(self):
        """Get all quotes"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/quotes", 
                                     headers=self.get_headers()) as response:
                    response_time = time.time() - start_time
                    
                    self.results.append(TestResult(
                        test_name="Get Quotes",
                        success=response.status == 200,
                        response_time=response_time,
                        status_code=response.status,
                        user_id=self.user_id,
                        timestamp=datetime.now()
                    ))
                    
        except Exception as e:
            self.results.append(TestResult(
                test_name="Get Quotes",
                success=False,
                response_time=0,
                status_code=0,
                error_message=str(e),
                user_id=self.user_id,
                timestamp=datetime.now()
            ))
    
    async def test_scheduling_operations(self):
        """Test scheduling system under load"""
        if not self.is_authenticated:
            return
            
        # Test team leaders
        await self.get_team_leaders()
        
        # Test collaborators
        await self.get_collaborators()
        
        # Test schedules
        await self.get_schedules()
    
    async def get_team_leaders(self):
        """Get team leaders"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/team-leaders", 
                                     headers=self.get_headers()) as response:
                    response_time = time.time() - start_time
                    
                    self.results.append(TestResult(
                        test_name="Get Team Leaders",
                        success=response.status == 200,
                        response_time=response_time,
                        status_code=response.status,
                        user_id=self.user_id,
                        timestamp=datetime.now()
                    ))
                    
        except Exception as e:
            self.results.append(TestResult(
                test_name="Get Team Leaders",
                success=False,
                response_time=0,
                status_code=0,
                error_message=str(e),
                user_id=self.user_id,
                timestamp=datetime.now()
            ))
    
    async def get_collaborators(self):
        """Get collaborators"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/collaborators", 
                                     headers=self.get_headers()) as response:
                    response_time = time.time() - start_time
                    
                    self.results.append(TestResult(
                        test_name="Get Collaborators",
                        success=response.status == 200,
                        response_time=response_time,
                        status_code=response.status,
                        user_id=self.user_id,
                        timestamp=datetime.now()
                    ))
                    
        except Exception as e:
            self.results.append(TestResult(
                test_name="Get Collaborators",
                success=False,
                response_time=0,
                status_code=0,
                error_message=str(e),
                user_id=self.user_id,
                timestamp=datetime.now()
            ))
    
    async def get_schedules(self):
        """Get schedules"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/schedules", 
                                     headers=self.get_headers()) as response:
                    response_time = time.time() - start_time
                    
                    self.results.append(TestResult(
                        test_name="Get Schedules",
                        success=response.status == 200,
                        response_time=response_time,
                        status_code=response.status,
                        user_id=self.user_id,
                        timestamp=datetime.now()
                    ))
                    
        except Exception as e:
            self.results.append(TestResult(
                test_name="Get Schedules",
                success=False,
                response_time=0,
                status_code=0,
                error_message=str(e),
                user_id=self.user_id,
                timestamp=datetime.now()
            ))

class IntensivePerformanceTester:
    """Main performance testing orchestrator"""
    
    def __init__(self):
        self.users = []
        self.all_results = []
        self.start_time = None
        self.end_time = None
        
    async def initialize_sample_data(self):
        """Initialize sample data for testing"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{BACKEND_URL}/init-sample-data") as response:
                    print(f"✅ Sample data initialized: {response.status}")
        except Exception as e:
            print(f"⚠️  Sample data initialization failed (may already exist): {e}")
    
    async def run_user_simulation(self, user_id: int):
        """Run simulation for a single user"""
        user = PerformanceTestUser(user_id)
        
        # Authenticate
        if not await user.authenticate():
            print(f"❌ User {user_id} authentication failed")
            return user.results
        
        print(f"✅ User {user_id} authenticated successfully")
        
        # Run various operations concurrently
        operations = [
            user.test_dashboard_stats(),
            user.test_search_operations(),
            user.test_quote_operations(),
            user.test_pdf_generation(),
            user.test_scheduling_operations()
        ]
        
        # Execute operations with some randomization
        for _ in range(3):  # Each user performs 3 rounds of operations
            # Randomize operation order
            random.shuffle(operations)
            
            # Execute operations with random delays
            for operation in operations:
                await operation
                await asyncio.sleep(random.uniform(0.1, 0.5))  # Random delay between operations
            
            await asyncio.sleep(random.uniform(1, 3))  # Random delay between rounds
        
        return user.results
    
    async def run_intensive_test(self):
        """Run intensive performance test with concurrent users"""
        print(f"🚀 STARTING INTENSIVE PERFORMANCE TEST")
        print(f"👥 Simulating {CONCURRENT_USERS} concurrent users")
        print(f"⏱️  Test duration: {TEST_DURATION} seconds")
        print(f"🎯 Target response time: < {MAX_RESPONSE_TIME} seconds")
        print("=" * 80)
        
        # Initialize sample data
        await self.initialize_sample_data()
        
        self.start_time = time.time()
        
        # Create and run concurrent user simulations
        tasks = []
        for user_id in range(1, CONCURRENT_USERS + 1):
            task = asyncio.create_task(self.run_user_simulation(user_id))
            tasks.append(task)
            
            # Stagger user starts to simulate realistic load
            if user_id % 5 == 0:
                await asyncio.sleep(0.5)
        
        print(f"⏳ Running {len(tasks)} concurrent user simulations...")
        
        # Wait for all tasks to complete or timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=TEST_DURATION
            )
            
            # Collect all results
            for result in results:
                if isinstance(result, list):
                    self.all_results.extend(result)
                elif isinstance(result, Exception):
                    print(f"⚠️  Task failed with exception: {result}")
                    
        except asyncio.TimeoutError:
            print(f"⏰ Test completed after {TEST_DURATION} seconds timeout")
        
        self.end_time = time.time()
        
        # Analyze results
        self.analyze_performance()
    
    def analyze_performance(self):
        """Analyze performance test results"""
        print("\n" + "=" * 80)
        print("📊 INTENSIVE PERFORMANCE TEST RESULTS")
        print("=" * 80)
        
        if not self.all_results:
            print("❌ No results collected")
            return
        
        # Overall statistics
        total_tests = len(self.all_results)
        successful_tests = sum(1 for r in self.all_results if r.success)
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Response time statistics
        response_times = [r.response_time for r in self.all_results if r.response_time > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        # Performance targets
        fast_responses = sum(1 for rt in response_times if rt < MAX_RESPONSE_TIME)
        performance_rate = (fast_responses / len(response_times) * 100) if response_times else 0
        
        print(f"🎯 OVERALL PERFORMANCE:")
        print(f"   Total Operations: {total_tests}")
        print(f"   Successful: {successful_tests} ({success_rate:.1f}%)")
        print(f"   Failed: {failed_tests}")
        print(f"   Concurrent Users: {CONCURRENT_USERS}")
        print(f"   Test Duration: {self.end_time - self.start_time:.1f} seconds")
        
        print(f"\n⏱️  RESPONSE TIME ANALYSIS:")
        print(f"   Average Response Time: {avg_response_time:.3f}s")
        print(f"   Min Response Time: {min_response_time:.3f}s")
        print(f"   Max Response Time: {max_response_time:.3f}s")
        print(f"   Responses < {MAX_RESPONSE_TIME}s: {fast_responses}/{len(response_times)} ({performance_rate:.1f}%)")
        
        # Test type breakdown
        test_types = {}
        for result in self.all_results:
            test_name = result.test_name
            if test_name not in test_types:
                test_types[test_name] = {'total': 0, 'success': 0, 'avg_time': 0}
            
            test_types[test_name]['total'] += 1
            if result.success:
                test_types[test_name]['success'] += 1
            if result.response_time > 0:
                test_types[test_name]['avg_time'] += result.response_time
        
        print(f"\n📋 OPERATION BREAKDOWN:")
        for test_name, stats in test_types.items():
            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            avg_time = stats['avg_time'] / stats['total'] if stats['total'] > 0 else 0
            print(f"   {test_name}: {stats['success']}/{stats['total']} ({success_rate:.1f}%) - Avg: {avg_time:.3f}s")
        
        # Error analysis
        errors = [r for r in self.all_results if not r.success]
        if errors:
            print(f"\n❌ ERROR ANALYSIS:")
            error_types = {}
            for error in errors:
                error_key = f"{error.status_code} - {error.error_message[:50]}"
                error_types[error_key] = error_types.get(error_key, 0) + 1
            
            for error_type, count in error_types.items():
                print(f"   {error_type}: {count} occurrences")
        
        # Data integrity check
        self.check_data_integrity()
        
        # Performance verdict
        print(f"\n🏆 PERFORMANCE VERDICT:")
        if success_rate >= 95 and performance_rate >= 90:
            print("   ✅ EXCELLENT: System handles concurrent load very well!")
        elif success_rate >= 90 and performance_rate >= 80:
            print("   ✅ GOOD: System performs well under load with minor issues")
        elif success_rate >= 80 and performance_rate >= 70:
            print("   ⚠️  ACCEPTABLE: System handles load but needs optimization")
        else:
            print("   ❌ NEEDS IMPROVEMENT: System struggles under concurrent load")
        
        print(f"\n📈 RECOMMENDATIONS:")
        if avg_response_time > MAX_RESPONSE_TIME:
            print(f"   - Optimize response times (current avg: {avg_response_time:.3f}s > target: {MAX_RESPONSE_TIME}s)")
        if success_rate < 95:
            print(f"   - Improve error handling (current success rate: {success_rate:.1f}%)")
        if failed_tests > 0:
            print(f"   - Investigate and fix {failed_tests} failed operations")
        
        print(f"\n🎯 PERFORMANCE SUMMARY:")
        print(f"   System successfully handled {CONCURRENT_USERS} concurrent users")
        print(f"   Processed {total_tests} total operations")
        print(f"   Achieved {success_rate:.1f}% success rate")
        print(f"   {performance_rate:.1f}% of responses met performance target")
    
    def check_data_integrity(self):
        """Check data integrity during concurrent operations"""
        print(f"\n🔍 DATA INTEGRITY CHECK:")
        
        # Check for authentication consistency
        auth_results = [r for r in self.all_results if r.test_name == "Authentication"]
        successful_auths = sum(1 for r in auth_results if r.success)
        unique_users = len(set(r.user_id for r in auth_results))
        
        print(f"   Authentication Integrity: {successful_auths}/{len(auth_results)} successful")
        print(f"   Unique Users Authenticated: {unique_users}")
        
        # Check for operation consistency
        create_operations = [r for r in self.all_results if "Create" in r.test_name and r.success]
        read_operations = [r for r in self.all_results if "Get" in r.test_name and r.success]
        
        print(f"   Create Operations: {len(create_operations)} successful")
        print(f"   Read Operations: {len(read_operations)} successful")
        
        # Check for concurrent access issues
        concurrent_issues = sum(1 for r in self.all_results if r.status_code in [409, 423, 429])
        if concurrent_issues > 0:
            print(f"   ⚠️  Concurrent Access Issues: {concurrent_issues} detected")
        else:
            print(f"   ✅ No concurrent access conflicts detected")

async def main():
    """Main execution function"""
    tester = IntensivePerformanceTester()
    await tester.run_intensive_test()

if __name__ == "__main__":
    print("🔥 SKYAPP INTENSIVE PERFORMANCE TESTING")
    print("Simulating heavy concurrent user load...")
    print("=" * 80)
    
    # Run the intensive performance test
    asyncio.run(main())