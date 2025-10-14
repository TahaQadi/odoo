"""
Performance Testing Script for ChemFactory MES/ERP
Tests system performance under load and stress conditions
"""

import asyncio
import aiohttp
import time
import statistics
from datetime import datetime
import json
import random

class PerformanceTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.results = {
            'api_tests': [],
            'load_tests': [],
            'stress_tests': [],
            'concurrent_tests': []
        }
    
    async def authenticate(self):
        """Authenticate and get token"""
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/v1/auth/login", data={
                "username": "admin",
                "password": "admin"
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data["access_token"]
                    return True
                return False
    
    async def test_api_endpoint(self, session, method: str, endpoint: str, **kwargs):
        """Test a single API endpoint"""
        headers = {"Authorization": f"Bearer {self.token}"}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        
        start_time = time.time()
        try:
            async with session.request(method, f"{self.base_url}{endpoint}", 
                                     headers=headers, **kwargs) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                return {
                    'endpoint': endpoint,
                    'method': method,
                    'status_code': response.status,
                    'response_time': response_time,
                    'success': 200 <= response.status < 300,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'method': method,
                'status_code': 0,
                'response_time': end_time - start_time,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def test_core_apis(self):
        """Test core API endpoints performance"""
        print("🔍 Testing Core API Performance...")
        
        endpoints = [
            ("GET", "/api/v1/products/"),
            ("GET", "/api/v1/manufacturing/orders"),
            ("GET", "/api/v1/batches/"),
            ("GET", "/api/v1/quality/checks"),
            ("GET", "/api/v1/monitoring/dashboard"),
            ("GET", "/api/v1/reports/production/summary"),
            ("GET", "/api/v1/reports/quality/trends"),
            ("GET", "/api/v1/reports/inventory/analysis"),
            ("GET", "/api/v1/reports/kpi/dashboard"),
            ("GET", "/health")
        ]
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for method, endpoint in endpoints:
                task = self.test_api_endpoint(session, method, endpoint)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            self.results['api_tests'].extend(results)
            
            # Print results
            for result in results:
                status = "✅" if result['success'] else "❌"
                print(f"  {status} {result['method']} {result['endpoint']}: "
                      f"{result['response_time']:.3f}s ({result['status_code']})")
    
    async def load_test_products(self, concurrent_requests: int = 10, total_requests: int = 100):
        """Load test product creation"""
        print(f"📊 Load Testing Product Creation ({concurrent_requests} concurrent, {total_requests} total)...")
        
        async def create_product(session, product_id):
            product_data = {
                "code": f"LOAD_TEST_{product_id:04d}",
                "name_en": f"Load Test Product {product_id}",
                "name_ar": f"منتج اختبار الحمل {product_id}",
                "product_type": "FINISHED_GOOD",
                "unit": "L",
                "density": 1.0,
                "hazard_class": "NONE",
                "storage_flag": "NORMAL",
                "is_active": True
            }
            
            return await self.test_api_endpoint(
                session, "POST", "/api/v1/products/", 
                json=product_data
            )
        
        async with aiohttp.ClientSession() as session:
            # Create semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(concurrent_requests)
            
            async def limited_create_product(product_id):
                async with semaphore:
                    return await create_product(session, product_id)
            
            # Execute requests
            start_time = time.time()
            tasks = [limited_create_product(i) for i in range(total_requests)]
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # Analyze results
            successful = [r for r in results if r['success']]
            failed = [r for r in results if not r['success']]
            response_times = [r['response_time'] for r in successful]
            
            total_time = end_time - start_time
            requests_per_second = total_requests / total_time
            
            print(f"  📈 Total time: {total_time:.2f}s")
            print(f"  📈 Requests/sec: {requests_per_second:.2f}")
            print(f"  ✅ Successful: {len(successful)}")
            print(f"  ❌ Failed: {len(failed)}")
            
            if response_times:
                print(f"  📊 Avg response time: {statistics.mean(response_times):.3f}s")
                print(f"  📊 Min response time: {min(response_times):.3f}s")
                print(f"  📊 Max response time: {max(response_times):.3f}s")
                print(f"  📊 95th percentile: {sorted(response_times)[int(len(response_times) * 0.95)]:.3f}s")
            
            self.results['load_tests'].extend(results)
    
    async def stress_test_monitoring(self, duration_seconds: int = 60):
        """Stress test monitoring endpoints"""
        print(f"⚡ Stress Testing Monitoring ({duration_seconds}s)...")
        
        endpoints = [
            "/api/v1/monitoring/dashboard",
            "/api/v1/monitoring/alerts",
            "/api/v1/monitoring/metrics"
        ]
        
        async def stress_worker(session, worker_id):
            results = []
            end_time = time.time() + duration_seconds
            
            while time.time() < end_time:
                for endpoint in endpoints:
                    result = await self.test_api_endpoint(session, "GET", endpoint)
                    result['worker_id'] = worker_id
                    results.append(result)
                    await asyncio.sleep(0.1)  # Small delay between requests
            
            return results
        
        async with aiohttp.ClientSession() as session:
            # Run multiple workers concurrently
            workers = 5
            tasks = [stress_worker(session, i) for i in range(workers)]
            all_results = await asyncio.gather(*tasks)
            
            # Flatten results
            results = []
            for worker_results in all_results:
                results.extend(worker_results)
            
            # Analyze results
            successful = [r for r in results if r['success']]
            failed = [r for r in results if not r['success']]
            response_times = [r['response_time'] for r in successful]
            
            print(f"  📊 Total requests: {len(results)}")
            print(f"  ✅ Successful: {len(successful)}")
            print(f"  ❌ Failed: {len(failed)}")
            print(f"  📊 Success rate: {len(successful)/len(results)*100:.1f}%")
            
            if response_times:
                print(f"  📊 Avg response time: {statistics.mean(response_times):.3f}s")
                print(f"  📊 Max response time: {max(response_times):.3f}s")
            
            self.results['stress_tests'].extend(results)
    
    async def test_concurrent_operations(self):
        """Test concurrent operations across different modules"""
        print("🔄 Testing Concurrent Operations...")
        
        async def concurrent_operations(session, operation_id):
            operations = [
                ("GET", "/api/v1/products/"),
                ("GET", "/api/v1/manufacturing/orders"),
                ("GET", "/api/v1/batches/"),
                ("GET", "/api/v1/quality/checks"),
                ("GET", "/api/v1/monitoring/dashboard"),
                ("GET", "/api/v1/reports/production/summary")
            ]
            
            results = []
            for method, endpoint in operations:
                result = await self.test_api_endpoint(session, method, endpoint)
                result['operation_id'] = operation_id
                results.append(result)
                await asyncio.sleep(0.05)  # Small delay between operations
            
            return results
        
        async with aiohttp.ClientSession() as session:
            # Run 20 concurrent operation sets
            tasks = [concurrent_operations(session, i) for i in range(20)]
            all_results = await asyncio.gather(*tasks)
            
            # Flatten results
            results = []
            for operation_results in all_results:
                results.extend(operation_results)
            
            # Analyze results
            successful = [r for r in results if r['success']]
            failed = [r for r in results if not r['success']]
            response_times = [r['response_time'] for r in successful]
            
            print(f"  📊 Total operations: {len(results)}")
            print(f"  ✅ Successful: {len(successful)}")
            print(f"  ❌ Failed: {len(failed)}")
            print(f"  📊 Success rate: {len(successful)/len(results)*100:.1f}%")
            
            if response_times:
                print(f"  📊 Avg response time: {statistics.mean(response_times):.3f}s")
                print(f"  📊 Max response time: {max(response_times):.3f}s")
            
            self.results['concurrent_tests'].extend(results)
    
    async def test_websocket_performance(self):
        """Test WebSocket performance"""
        print("🔌 Testing WebSocket Performance...")
        
        try:
            import websockets
            
            async def websocket_test():
                uri = f"ws://localhost:8000/api/v1/monitoring/ws"
                start_time = time.time()
                message_count = 0
                
                try:
                    async with websockets.connect(uri) as websocket:
                        # Listen for messages for 30 seconds
                        while time.time() - start_time < 30:
                            try:
                                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                                message_count += 1
                                data = json.loads(message)
                                print(f"  📨 Message {message_count}: {data.get('timestamp', 'N/A')}")
                            except asyncio.TimeoutError:
                                print("  ⏰ WebSocket timeout")
                                break
                except Exception as e:
                    print(f"  ❌ WebSocket error: {e}")
                    return
                
                duration = time.time() - start_time
                print(f"  📊 Duration: {duration:.1f}s")
                print(f"  📊 Messages received: {message_count}")
                print(f"  📊 Messages/sec: {message_count/duration:.2f}")
            
            await websocket_test()
            
        except ImportError:
            print("  ⚠️ WebSocket testing requires 'websockets' package")
        except Exception as e:
            print(f"  ❌ WebSocket test failed: {e}")
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n📊 Performance Test Report")
        print("=" * 50)
        
        all_tests = []
        all_tests.extend(self.results['api_tests'])
        all_tests.extend(self.results['load_tests'])
        all_tests.extend(self.results['stress_tests'])
        all_tests.extend(self.results['concurrent_tests'])
        
        if not all_tests:
            print("No test results available")
            return
        
        # Overall statistics
        successful = [t for t in all_tests if t['success']]
        failed = [t for t in all_tests if not t['success']]
        response_times = [t['response_time'] for t in successful]
        
        print(f"📈 Total Tests: {len(all_tests)}")
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"📊 Success Rate: {len(successful)/len(all_tests)*100:.1f}%")
        
        if response_times:
            print(f"📊 Average Response Time: {statistics.mean(response_times):.3f}s")
            print(f"📊 Min Response Time: {min(response_times):.3f}s")
            print(f"📊 Max Response Time: {max(response_times):.3f}s")
            print(f"📊 95th Percentile: {sorted(response_times)[int(len(response_times) * 0.95)]:.3f}s")
        
        # Performance recommendations
        print("\n🎯 Performance Recommendations:")
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        if avg_response_time > 1.0:
            print("  ⚠️ Average response time is high (>1s). Consider optimization.")
        else:
            print("  ✅ Response times are within acceptable range.")
        
        success_rate = len(successful) / len(all_tests) * 100
        if success_rate < 95:
            print("  ⚠️ Success rate is below 95%. Check error handling.")
        else:
            print("  ✅ Success rate is excellent.")
        
        # Save detailed results
        with open('performance_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n💾 Detailed results saved to performance_results.json")
    
    async def run_all_tests(self):
        """Run all performance tests"""
        print("🚀 Starting ChemFactory Performance Testing Suite")
        print("=" * 60)
        
        # Authenticate
        if not await self.authenticate():
            print("❌ Authentication failed. Cannot run tests.")
            return
        
        print("✅ Authentication successful")
        
        # Run tests
        await self.test_core_apis()
        await self.load_test_products(concurrent_requests=5, total_requests=50)
        await self.stress_test_monitoring(duration_seconds=30)
        await self.test_concurrent_operations()
        await self.test_websocket_performance()
        
        # Generate report
        self.generate_performance_report()
        
        print("\n🎉 Performance testing completed!")

async def main():
    tester = PerformanceTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
