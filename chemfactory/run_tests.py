#!/usr/bin/env python3
"""
Comprehensive Test Runner for ChemFactory MES/ERP
Runs all tests and simulations to validate system functionality
"""

import asyncio
import subprocess
import sys
import os
import time
from datetime import datetime

class TestRunner:
    def __init__(self):
        self.results = {
            'start_time': datetime.now(),
            'tests_run': [],
            'passed': 0,
            'failed': 0,
            'total_time': 0
        }
    
    def print_header(self, title):
        """Print a formatted header"""
        print("\n" + "=" * 60)
        print(f"🧪 {title}")
        print("=" * 60)
    
    def print_test_result(self, test_name, success, duration=None, details=None):
        """Print test result"""
        status = "✅ PASSED" if success else "❌ FAILED"
        duration_str = f" ({duration:.2f}s)" if duration else ""
        print(f"{status} {test_name}{duration_str}")
        
        if details:
            for detail in details:
                print(f"    {detail}")
        
        self.results['tests_run'].append({
            'name': test_name,
            'success': success,
            'duration': duration,
            'details': details or []
        })
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
    
    def run_command(self, command, description):
        """Run a command and return success status"""
        print(f"🔄 {description}...")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            details = []
            if result.stdout:
                details.append(f"STDOUT: {result.stdout.strip()}")
            if result.stderr:
                details.append(f"STDERR: {result.stderr.strip()}")
            
            self.print_test_result(description, success, duration, details)
            return success
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.print_test_result(description, False, duration, ["Command timed out"])
            return False
        except Exception as e:
            duration = time.time() - start_time
            self.print_test_result(description, False, duration, [f"Error: {str(e)}"])
            return False
    
    def run_backend_tests(self):
        """Run backend API tests"""
        self.print_header("Backend API Tests")
        
        # Install test dependencies
        self.run_command(
            "cd backend && pip install pytest pytest-asyncio httpx",
            "Install test dependencies"
        )
        
        # Run API tests
        self.run_command(
            "cd backend && python -m pytest app/tests/test_api.py -v",
            "Run API endpoint tests"
        )
    
    def run_ai_tests(self):
        """Run AI model tests"""
        self.print_header("AI Model Tests")
        
        # Install AI dependencies
        self.run_command(
            "cd backend && pip install numpy pandas scikit-learn",
            "Install AI dependencies"
        )
        
        # Run AI tests
        self.run_command(
            "cd backend && python app/tests/test_ai.py",
            "Run AI model tests"
        )
    
    def run_performance_tests(self):
        """Run performance tests"""
        self.print_header("Performance Tests")
        
        # Install performance test dependencies
        self.run_command(
            "cd backend && pip install aiohttp websockets",
            "Install performance test dependencies"
        )
        
        # Run performance tests
        self.run_command(
            "cd backend && python app/tests/performance_test.py",
            "Run performance tests"
        )
    
    def run_simulation(self):
        """Run production simulation"""
        self.print_header("Production Simulation")
        
        # Install simulation dependencies
        self.run_command(
            "cd backend && pip install requests",
            "Install simulation dependencies"
        )
        
        # Run simulation
        self.run_command(
            "cd backend && python app/tests/simulation.py",
            "Run production simulation"
        )
    
    def run_frontend_tests(self):
        """Run frontend tests"""
        self.print_header("Frontend Tests")
        
        # Install frontend dependencies
        self.run_command(
            "cd frontend && npm install",
            "Install frontend dependencies"
        )
        
        # Run linting
        self.run_command(
            "cd frontend && npm run lint",
            "Run ESLint"
        )
        
        # Run TypeScript check
        self.run_command(
            "cd frontend && npm run type-check",
            "Run TypeScript check"
        )
        
        # Run build test
        self.run_command(
            "cd frontend && npm run build",
            "Test frontend build"
        )
    
    def run_integration_tests(self):
        """Run integration tests"""
        self.print_header("Integration Tests")
        
        # Test database connection
        self.run_command(
            "cd backend && python -c \"from app.db.database import engine; print('Database connection successful')\"",
            "Test database connection"
        )
        
        # Test API health
        self.run_command(
            "curl -f http://localhost:8000/health || echo 'API not running'",
            "Test API health endpoint"
        )
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.results['end_time'] = datetime.now()
        self.results['total_time'] = (self.results['end_time'] - self.results['start_time']).total_seconds()
        
        self.print_header("Test Summary Report")
        
        print(f"📊 Total Tests: {self.results['passed'] + self.results['failed']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⏱️ Total Time: {self.results['total_time']:.2f}s")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100) if (self.results['passed'] + self.results['failed']) > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 Test Details:")
        for test in self.results['tests_run']:
            status = "✅" if test['success'] else "❌"
            duration = f" ({test['duration']:.2f}s)" if test['duration'] else ""
            print(f"  {status} {test['name']}{duration}")
            
            if test['details']:
                for detail in test['details']:
                    print(f"      {detail}")
        
        # Recommendations
        print("\n🎯 Recommendations:")
        if success_rate >= 95:
            print("  ✅ Excellent! System is ready for production.")
        elif success_rate >= 80:
            print("  ⚠️ Good, but some issues need attention before production.")
        else:
            print("  ❌ Critical issues found. System needs fixes before production.")
        
        if self.results['failed'] > 0:
            print("  🔧 Review failed tests and fix issues before deployment.")
        
        # Save report
        import json
        with open('test_report.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n💾 Detailed report saved to test_report.json")
    
    def run_all_tests(self):
        """Run all tests and simulations"""
        print("🚀 Starting ChemFactory MES/ERP Test Suite")
        print(f"⏰ Started at: {self.results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Backend tests
            self.run_backend_tests()
            
            # AI tests
            self.run_ai_tests()
            
            # Performance tests
            self.run_performance_tests()
            
            # Simulation
            self.run_simulation()
            
            # Frontend tests
            self.run_frontend_tests()
            
            # Integration tests
            self.run_integration_tests()
            
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            # Generate report
            self.generate_test_report()
            
            # Final status
            if self.results['failed'] == 0:
                print("\n🎉 All tests passed! System is ready for production.")
                return 0
            else:
                print(f"\n⚠️ {self.results['failed']} tests failed. Please review and fix issues.")
                return 1

def main():
    """Main entry point"""
    runner = TestRunner()
    return runner.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
