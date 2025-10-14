"""
Production Simulation Script for ChemFactory MES/ERP
Simulates realistic production scenarios to test system performance
"""

import asyncio
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
import time

class ProductionSimulator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.products = []
        self.batches = []
        self.manufacturing_orders = []
        
    async def authenticate(self, username: str = "admin", password: str = "admin"):
        """Authenticate with the system"""
        response = self.session.post(f"{self.base_url}/api/v1/auth/login", data={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            print("✅ Authentication successful")
            return True
        else:
            print("❌ Authentication failed")
            return False
    
    async def create_test_products(self, count: int = 10):
        """Create test products for simulation"""
        print(f"🏭 Creating {count} test products...")
        
        product_types = ["RAW_MATERIAL", "INTERMEDIATE", "FINISHED_GOOD"]
        hazard_classes = ["NONE", "FLAMMABLE", "TOXIC", "CORROSIVE"]
        units = ["L", "kg", "g", "ml"]
        
        for i in range(count):
            product_data = {
                "code": f"SIM{i+1:03d}",
                "name_en": f"Simulation Product {i+1}",
                "name_ar": f"منتج محاكاة {i+1}",
                "product_type": random.choice(product_types),
                "unit": random.choice(units),
                "density": round(random.uniform(0.8, 2.0), 2),
                "hazard_class": random.choice(hazard_classes),
                "storage_flag": "NORMAL",
                "is_active": True
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/products/", json=product_data)
            if response.status_code == 200:
                self.products.append(response.json())
                print(f"  ✅ Created product: {product_data['code']}")
            else:
                print(f"  ❌ Failed to create product: {product_data['code']}")
    
    async def simulate_manufacturing_orders(self, count: int = 5):
        """Simulate manufacturing order creation and processing"""
        print(f"📋 Simulating {count} manufacturing orders...")
        
        for i in range(count):
            if not self.products:
                print("  ⚠️ No products available for manufacturing orders")
                break
                
            product = random.choice(self.products)
            mo_data = {
                "product_id": product["id"],
                "bom_id": 1,  # Assuming BOM exists
                "target_quantity": round(random.uniform(50, 500), 2),
                "planned_start_date": (datetime.now() + timedelta(hours=random.randint(1, 24))).isoformat(),
                "planned_end_date": (datetime.now() + timedelta(hours=random.randint(25, 48))).isoformat(),
                "priority": random.randint(1, 3)
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/manufacturing/orders", json=mo_data)
            if response.status_code == 200:
                mo = response.json()
                self.manufacturing_orders.append(mo)
                print(f"  ✅ Created MO: {mo['mo_number']} for {product['name_en']}")
                
                # Start some orders
                if random.random() < 0.7:  # 70% chance to start
                    await self.start_manufacturing_order(mo["id"])
            else:
                print(f"  ❌ Failed to create manufacturing order")
    
    async def start_manufacturing_order(self, mo_id: int):
        """Start a manufacturing order"""
        response = self.session.post(f"{self.base_url}/api/v1/manufacturing/orders/{mo_id}/start")
        if response.status_code == 200:
            print(f"    🚀 Started MO {mo_id}")
        else:
            print(f"    ❌ Failed to start MO {mo_id}")
    
    async def simulate_batch_processing(self, count: int = 15):
        """Simulate batch creation and processing"""
        print(f"🔄 Simulating {count} batch processes...")
        
        for i in range(count):
            if not self.products:
                print("  ⚠️ No products available for batches")
                break
                
            product = random.choice(self.products)
            batch_data = {
                "product_id": product["id"],
                "target_quantity": round(random.uniform(20, 200), 2),
                "status": "PLANNED"
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/batches/", json=batch_data)
            if response.status_code == 200:
                batch = response.json()
                self.batches.append(batch)
                print(f"  ✅ Created batch: {batch['batch_number']}")
                
                # Process some batches
                if random.random() < 0.8:  # 80% chance to process
                    await self.process_batch(batch["id"])
            else:
                print(f"  ❌ Failed to create batch")
    
    async def process_batch(self, batch_id: int):
        """Process a batch through its lifecycle"""
        # Start batch
        response = self.session.post(f"{self.base_url}/api/v1/batches/{batch_id}/start")
        if response.status_code == 200:
            print(f"    🚀 Started batch {batch_id}")
            
            # Simulate processing time
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            # Complete batch
            actual_quantity = round(random.uniform(18, 22), 2)  # Simulate some variance
            response = self.session.post(f"{self.base_url}/api/v1/batches/{batch_id}/complete", 
                                       params={"actual_quantity": actual_quantity})
            if response.status_code == 200:
                print(f"    ✅ Completed batch {batch_id} with {actual_quantity} units")
                
                # Create quality checks
                await self.create_quality_checks(batch_id)
            else:
                print(f"    ❌ Failed to complete batch {batch_id}")
        else:
            print(f"    ❌ Failed to start batch {batch_id}")
    
    async def create_quality_checks(self, batch_id: int):
        """Create quality checks for a batch"""
        quality_tests = [
            {"name_en": "pH Test", "name_ar": "اختبار الحموضة", "method": "pH Meter", "target": 7.0, "tolerance": 0.5},
            {"name_en": "Viscosity Test", "name_ar": "اختبار اللزوجة", "method": "Viscometer", "target": 100.0, "tolerance": 10.0},
            {"name_en": "Color Test", "name_ar": "اختبار اللون", "method": "Colorimeter", "target": 50.0, "tolerance": 5.0},
            {"name_en": "Density Test", "name_ar": "اختبار الكثافة", "method": "Densimeter", "target": 1.0, "tolerance": 0.05}
        ]
        
        for test in random.sample(quality_tests, random.randint(2, 4)):
            qc_data = {
                "batch_id": batch_id,
                "test_name_en": test["name_en"],
                "test_name_ar": test["name_ar"],
                "test_method": test["method"],
                "target_value": test["target"],
                "tolerance_min": test["tolerance"],
                "tolerance_max": test["tolerance"],
                "unit": "pH" if "pH" in test["name_en"] else "cP" if "Viscosity" in test["name_en"] else "units",
                "status": "PENDING"
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/quality/checks", json=qc_data)
            if response.status_code == 200:
                qc = response.json()
                print(f"      🧪 Created QC: {test['name_en']} for batch {batch_id}")
                
                # Perform quality test
                await self.perform_quality_test(qc["id"], test)
            else:
                print(f"      ❌ Failed to create QC: {test['name_en']}")
    
    async def perform_quality_test(self, qc_id: int, test_config: Dict):
        """Perform a quality test"""
        # Simulate test result with some variance
        actual_value = test_config["target"] + random.uniform(-test_config["tolerance"], test_config["tolerance"])
        actual_value = round(actual_value, 2)
        
        response = self.session.post(f"{self.base_url}/api/v1/quality/checks/{qc_id}/test",
                                   params={"actual_value": actual_value, "notes": "Simulated test result"})
        if response.status_code == 200:
            result = response.json()
            print(f"        ✅ QC {qc_id}: {actual_value} ({result['result']})")
        else:
            print(f"        ❌ Failed to perform QC {qc_id}")
    
    async def simulate_real_time_monitoring(self, duration_minutes: int = 5):
        """Simulate real-time monitoring data"""
        print(f"📊 Simulating real-time monitoring for {duration_minutes} minutes...")
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            # Get monitoring dashboard
            response = self.session.get(f"{self.base_url}/api/v1/monitoring/dashboard")
            if response.status_code == 200:
                data = response.json()
                print(f"  📈 Production: {data['production']['active_batches']} active, "
                      f"{data['production']['completed_today']} completed today")
                print(f"  🎯 Quality: {data['quality']['pass_rate']}% pass rate, "
                      f"{data['quality']['pending_tests']} pending")
                print(f"  📦 Inventory: ${data['inventory']['total_value']:,.0f} value, "
                      f"{data['inventory']['low_stock_items']} low stock")
                print(f"  ⚙️ Equipment: {data['equipment']['running_machines']} running, "
                      f"{data['equipment']['efficiency']}% efficiency")
            
            # Get alerts
            response = self.session.get(f"{self.base_url}/api/v1/monitoring/alerts")
            if response.status_code == 200:
                alerts = response.json()
                if alerts['total_alerts'] > 0:
                    print(f"  🚨 Alerts: {alerts['total_alerts']} total, "
                          f"{alerts['critical_alerts']} critical")
            
            await asyncio.sleep(10)  # Update every 10 seconds
    
    async def generate_reports(self):
        """Generate various reports"""
        print("📊 Generating reports...")
        
        reports = [
            ("Production Summary", "/api/v1/reports/production/summary"),
            ("Quality Trends", "/api/v1/reports/quality/trends"),
            ("Inventory Analysis", "/api/v1/reports/inventory/analysis"),
            ("KPI Dashboard", "/api/v1/reports/kpi/dashboard")
        ]
        
        for report_name, endpoint in reports:
            response = self.session.get(f"{self.base_url}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ {report_name}: Generated successfully")
                # Print key metrics
                if "summary" in data:
                    print(f"    📈 Summary: {data['summary']}")
                elif "overall_metrics" in data:
                    print(f"    📈 Metrics: {data['overall_metrics']}")
            else:
                print(f"  ❌ {report_name}: Failed to generate")
    
    async def run_full_simulation(self):
        """Run complete production simulation"""
        print("🚀 Starting ChemFactory Production Simulation")
        print("=" * 50)
        
        # Authenticate
        if not await self.authenticate():
            return
        
        # Create test data
        await self.create_test_products(15)
        await self.simulate_manufacturing_orders(8)
        await self.simulate_batch_processing(20)
        
        # Generate reports
        await self.generate_reports()
        
        # Simulate real-time monitoring
        await self.simulate_real_time_monitoring(2)
        
        print("=" * 50)
        print("✅ Simulation completed successfully!")
        print(f"📊 Created: {len(self.products)} products, {len(self.manufacturing_orders)} MOs, {len(self.batches)} batches")

async def main():
    simulator = ProductionSimulator()
    await simulator.run_full_simulation()

if __name__ == "__main__":
    asyncio.run(main())
