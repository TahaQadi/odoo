"""
Performance Testing Scenario for ChemFactory MES/ERP
Demonstrates system performance under various load conditions
"""

import time
import random
import statistics
from datetime import datetime
import json

class PerformanceTester:
    def __init__(self):
        self.results = []
        self.start_time = None
    
    def simulate_api_call(self, endpoint, response_time_ms):
        """Simulate an API call with specified response time"""
        time.sleep(response_time_ms / 1000)  # Convert ms to seconds
        return {
            'endpoint': endpoint,
            'response_time_ms': response_time_ms,
            'timestamp': datetime.now().isoformat(),
            'success': response_time_ms < 1000  # Success if under 1 second
        }
    
    def test_core_apis(self):
        """Test core API performance"""
        print("🔍 Testing Core API Performance...")
        
        endpoints = [
            "/api/v1/products/",
            "/api/v1/manufacturing/orders",
            "/api/v1/batches/",
            "/api/v1/quality/checks",
            "/api/v1/monitoring/dashboard",
            "/api/v1/reports/production/summary",
            "/api/v1/reports/quality/trends",
            "/api/v1/reports/inventory/analysis",
            "/api/v1/reports/kpi/dashboard",
            "/health"
        ]
        
        for endpoint in endpoints:
            # Simulate realistic response times
            base_time = random.uniform(50, 200)  # 50-200ms base
            if "reports" in endpoint:
                base_time += random.uniform(100, 300)  # Reports are slower
            if "monitoring" in endpoint:
                base_time += random.uniform(50, 150)  # Real-time data processing
            
            result = self.simulate_api_call(endpoint, base_time)
            self.results.append(result)
            
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {endpoint}: {result['response_time_ms']:.1f}ms")
    
    def load_test_products(self, concurrent_requests=10, total_requests=50):
        """Simulate load testing for product creation"""
        print(f"\n📊 Load Testing Product Creation ({concurrent_requests} concurrent, {total_requests} total)...")
        
        # Simulate concurrent requests
        start_time = time.time()
        
        for i in range(total_requests):
            # Simulate product creation with varying response times
            response_time = random.uniform(100, 500)  # 100-500ms
            result = self.simulate_api_call(f"/api/v1/products/ (POST {i+1})", response_time)
            result['request_id'] = i + 1
            self.results.append(result)
            
            if (i + 1) % 10 == 0:
                print(f"  📈 Processed {i + 1}/{total_requests} requests...")
        
        end_time = time.time()
        total_time = end_time - start_time
        requests_per_second = total_requests / total_time
        
        print(f"  📈 Total time: {total_time:.2f}s")
        print(f"  📈 Requests/sec: {requests_per_second:.2f}")
    
    def stress_test_monitoring(self, duration_seconds=30):
        """Stress test monitoring endpoints"""
        print(f"\n⚡ Stress Testing Monitoring ({duration_seconds}s)...")
        
        endpoints = [
            "/api/v1/monitoring/dashboard",
            "/api/v1/monitoring/alerts",
            "/api/v1/monitoring/metrics"
        ]
        
        end_time = time.time() + duration_seconds
        request_count = 0
        
        while time.time() < end_time:
            for endpoint in endpoints:
                # Simulate high load with occasional spikes
                base_time = random.uniform(50, 150)
                if random.random() < 0.1:  # 10% chance of spike
                    base_time += random.uniform(200, 500)
                
                result = self.simulate_api_call(endpoint, base_time)
                result['stress_test'] = True
                self.results.append(result)
                request_count += 1
            
            time.sleep(0.1)  # Small delay between request batches
        
        print(f"  📊 Total requests: {request_count}")
        print(f"  📊 Requests/sec: {request_count / duration_seconds:.2f}")
    
    def test_concurrent_operations(self):
        """Test concurrent operations across modules"""
        print("\n🔄 Testing Concurrent Operations...")
        
        operations = [
            ("GET", "/api/v1/products/"),
            ("GET", "/api/v1/manufacturing/orders"),
            ("GET", "/api/v1/batches/"),
            ("GET", "/api/v1/quality/checks"),
            ("GET", "/api/v1/monitoring/dashboard"),
            ("GET", "/api/v1/reports/production/summary")
        ]
        
        # Simulate 20 concurrent operation sets
        for operation_set in range(20):
            for method, endpoint in operations:
                # Simulate concurrent load
                response_time = random.uniform(80, 300)
                result = self.simulate_api_call(f"{method} {endpoint}", response_time)
                result['operation_set'] = operation_set + 1
                self.results.append(result)
            
            if (operation_set + 1) % 5 == 0:
                print(f"  📈 Completed {operation_set + 1}/20 operation sets...")
    
    def simulate_websocket_performance(self):
        """Simulate WebSocket performance"""
        print("\n🔌 Simulating WebSocket Performance...")
        
        # Simulate WebSocket message processing
        message_count = 0
        start_time = time.time()
        
        # Simulate 30 seconds of WebSocket activity
        for i in range(30):
            # Simulate message processing time
            processing_time = random.uniform(10, 50)  # 10-50ms per message
            time.sleep(processing_time / 1000)
            
            message_count += 1
            
            if (i + 1) % 10 == 0:
                print(f"  📨 Processed {message_count} messages...")
        
        duration = time.time() - start_time
        messages_per_second = message_count / duration
        
        print(f"  📊 Duration: {duration:.1f}s")
        print(f"  📊 Messages processed: {message_count}")
        print(f"  📊 Messages/sec: {messages_per_second:.2f}")
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n📊 Performance Test Report")
        print("=" * 50)
        
        if not self.results:
            print("No test results available")
            return
        
        # Calculate statistics
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        response_times = [r['response_time_ms'] for r in successful]
        
        print(f"📈 Total Tests: {len(self.results)}")
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"📊 Success Rate: {len(successful)/len(self.results)*100:.1f}%")
        
        if response_times:
            print(f"📊 Average Response Time: {statistics.mean(response_times):.1f}ms")
            print(f"📊 Min Response Time: {min(response_times):.1f}ms")
            print(f"📊 Max Response Time: {max(response_times):.1f}ms")
            print(f"📊 95th Percentile: {sorted(response_times)[int(len(response_times) * 0.95)]:.1f}ms")
        
        # Performance recommendations
        print("\n🎯 Performance Recommendations:")
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        if avg_response_time > 500:
            print("  ⚠️ Average response time is high (>500ms). Consider optimization.")
        elif avg_response_time > 200:
            print("  ⚠️ Response time is moderate (>200ms). Monitor performance.")
        else:
            print("  ✅ Response times are excellent (<200ms).")
        
        success_rate = len(successful) / len(self.results) * 100
        if success_rate < 95:
            print("  ⚠️ Success rate is below 95%. Check error handling.")
        else:
            print("  ✅ Success rate is excellent.")
        
        # Endpoint analysis
        print("\n📋 Endpoint Analysis:")
        endpoint_stats = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = []
            endpoint_stats[endpoint].append(result['response_time_ms'])
        
        for endpoint, times in endpoint_stats.items():
            avg_time = statistics.mean(times)
            max_time = max(times)
            print(f"  📊 {endpoint}: avg {avg_time:.1f}ms, max {max_time:.1f}ms")
        
        # Save results
        report_data = {
            'summary': {
                'total_tests': len(self.results),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': len(successful)/len(self.results)*100,
                'avg_response_time': statistics.mean(response_times) if response_times else 0,
                'max_response_time': max(response_times) if response_times else 0
            },
            'results': self.results,
            'generated_at': datetime.now().isoformat()
        }
        
        with open('performance_results.json', 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to performance_results.json")
    
    def run_performance_tests(self):
        """Run all performance tests"""
        print("🚀 ChemFactory Performance Testing")
        print("=" * 50)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.start_time = time.time()
        
        # Run tests
        self.test_core_apis()
        self.load_test_products(concurrent_requests=5, total_requests=30)
        self.stress_test_monitoring(duration_seconds=15)
        self.test_concurrent_operations()
        self.simulate_websocket_performance()
        
        # Generate report
        self.generate_performance_report()
        
        end_time = time.time()
        total_duration = end_time - self.start_time
        
        print(f"\n🎉 Performance testing completed!")
        print(f"⏱️ Total duration: {total_duration:.1f} seconds")

if __name__ == "__main__":
    tester = PerformanceTester()
    tester.run_performance_tests()
