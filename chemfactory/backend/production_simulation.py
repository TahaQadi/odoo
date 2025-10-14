"""
Production Simulation Scenario for ChemFactory MES/ERP
Demonstrates realistic production workflows and data generation
"""

import random
import json
from datetime import datetime, timedelta
import time

class ProductionSimulator:
    def __init__(self):
        self.products = []
        self.batches = []
        self.manufacturing_orders = []
        self.quality_checks = []
        self.start_time = datetime.now()
    
    def simulate_product_creation(self, count=10):
        """Simulate product creation"""
        print(f"🏭 Creating {count} products...")
        
        product_types = ["RAW_MATERIAL", "INTERMEDIATE", "FINISHED_GOOD"]
        hazard_classes = ["NONE", "FLAMMABLE", "TOXIC", "CORROSIVE"]
        units = ["L", "kg", "g", "ml"]
        
        for i in range(count):
            product = {
                "id": i + 1,
                "code": f"PROD{i+1:03d}",
                "name_en": f"Chemical Product {i+1}",
                "name_ar": f"منتج كيميائي {i+1}",
                "product_type": random.choice(product_types),
                "unit": random.choice(units),
                "density": round(random.uniform(0.8, 2.0), 2),
                "hazard_class": random.choice(hazard_classes),
                "storage_flag": "NORMAL",
                "is_active": True,
                "created_at": datetime.now().isoformat()
            }
            self.products.append(product)
            print(f"  ✅ Created: {product['code']} - {product['name_en']}")
            time.sleep(0.1)  # Simulate processing time
    
    def simulate_manufacturing_orders(self, count=5):
        """Simulate manufacturing order creation"""
        print(f"\n📋 Creating {count} manufacturing orders...")
        
        for i in range(count):
            if not self.products:
                print("  ⚠️ No products available")
                break
            
            product = random.choice(self.products)
            mo = {
                "id": i + 1,
                "mo_number": f"MO{datetime.now().strftime('%Y%m%d')}{i+1:04d}",
                "product_id": product["id"],
                "product_name": product["name_en"],
                "target_quantity": round(random.uniform(50, 500), 2),
                "status": "PLANNED",
                "priority": random.randint(1, 3),
                "planned_start_date": (datetime.now() + timedelta(hours=random.randint(1, 24))).isoformat(),
                "planned_end_date": (datetime.now() + timedelta(hours=random.randint(25, 48))).isoformat(),
                "created_at": datetime.now().isoformat()
            }
            self.manufacturing_orders.append(mo)
            print(f"  ✅ Created: {mo['mo_number']} for {product['name_en']} ({mo['target_quantity']} {product['unit']})")
            time.sleep(0.1)
    
    def simulate_batch_processing(self, count=15):
        """Simulate batch creation and processing"""
        print(f"\n🔄 Processing {count} batches...")
        
        for i in range(count):
            if not self.products:
                print("  ⚠️ No products available")
                break
            
            product = random.choice(self.products)
            batch = {
                "id": i + 1,
                "batch_number": f"B{datetime.now().strftime('%Y%m%d')}{i+1:04d}",
                "product_id": product["id"],
                "product_name": product["name_en"],
                "target_quantity": round(random.uniform(20, 200), 2),
                "actual_quantity": None,
                "status": "PLANNED",
                "start_date": None,
                "end_date": None,
                "created_at": datetime.now().isoformat()
            }
            
            # Process batch (80% chance to process)
            if random.random() < 0.8:
                batch["status"] = "IN_PROGRESS"
                batch["start_date"] = datetime.now().isoformat()
                print(f"  🚀 Started: {batch['batch_number']} - {product['name_en']}")
                time.sleep(0.2)
                
                # Complete batch (90% chance to complete)
                if random.random() < 0.9:
                    batch["status"] = "COMPLETED"
                    batch["actual_quantity"] = round(batch["target_quantity"] * random.uniform(0.95, 1.05), 2)
                    batch["end_date"] = datetime.now().isoformat()
                    print(f"    ✅ Completed: {batch['batch_number']} - {batch['actual_quantity']} {product['unit']}")
                    
                    # Create quality checks for completed batch
                    self.create_quality_checks(batch["id"])
                else:
                    batch["status"] = "ON_HOLD"
                    print(f"    ⏸️ On Hold: {batch['batch_number']}")
            else:
                print(f"  📝 Planned: {batch['batch_number']} - {product['name_en']}")
            
            self.batches.append(batch)
            time.sleep(0.1)
    
    def create_quality_checks(self, batch_id):
        """Create quality checks for a batch"""
        quality_tests = [
            {"name_en": "pH Test", "name_ar": "اختبار الحموضة", "method": "pH Meter", "target": 7.0, "tolerance": 0.5},
            {"name_en": "Viscosity Test", "name_ar": "اختبار اللزوجة", "method": "Viscometer", "target": 100.0, "tolerance": 10.0},
            {"name_en": "Color Test", "name_ar": "اختبار اللون", "method": "Colorimeter", "target": 50.0, "tolerance": 5.0},
            {"name_en": "Density Test", "name_ar": "اختبار الكثافة", "method": "Densimeter", "target": 1.0, "tolerance": 0.05}
        ]
        
        # Create 2-4 random quality tests
        selected_tests = random.sample(quality_tests, random.randint(2, 4))
        
        for test in selected_tests:
            qc = {
                "id": len(self.quality_checks) + 1,
                "batch_id": batch_id,
                "test_name_en": test["name_en"],
                "test_name_ar": test["name_ar"],
                "test_method": test["method"],
                "target_value": test["target"],
                "tolerance_min": test["tolerance"],
                "tolerance_max": test["tolerance"],
                "actual_value": None,
                "unit": "pH" if "pH" in test["name_en"] else "cP" if "Viscosity" in test["name_en"] else "units",
                "status": "PENDING",
                "tested_at": None,
                "created_at": datetime.now().isoformat()
            }
            
            # Perform test (95% chance to pass)
            if random.random() < 0.95:
                qc["status"] = "PASS"
                qc["actual_value"] = round(test["target"] + random.uniform(-test["tolerance"], test["tolerance"]), 2)
                qc["tested_at"] = datetime.now().isoformat()
                print(f"      🧪 QC: {test['name_en']} - {qc['actual_value']} (PASS)")
            else:
                qc["status"] = "FAIL"
                qc["actual_value"] = round(test["target"] + random.uniform(-test["tolerance"] * 2, test["tolerance"] * 2), 2)
                qc["tested_at"] = datetime.now().isoformat()
                print(f"      🧪 QC: {test['name_en']} - {qc['actual_value']} (FAIL)")
            
            self.quality_checks.append(qc)
            time.sleep(0.05)
    
    def generate_reports(self):
        """Generate various reports"""
        print(f"\n📊 Generating reports...")
        
        # Production Summary
        completed_batches = len([b for b in self.batches if b["status"] == "COMPLETED"])
        total_batches = len(self.batches)
        completion_rate = (completed_batches / total_batches * 100) if total_batches > 0 else 0
        
        print(f"  📈 Production Summary:")
        print(f"    Total Batches: {total_batches}")
        print(f"    Completed: {completed_batches}")
        print(f"    Completion Rate: {completion_rate:.1f}%")
        
        # Quality Summary
        total_qc = len(self.quality_checks)
        passed_qc = len([qc for qc in self.quality_checks if qc["status"] == "PASS"])
        failed_qc = len([qc for qc in self.quality_checks if qc["status"] == "FAIL"])
        pass_rate = (passed_qc / total_qc * 100) if total_qc > 0 else 0
        
        print(f"  🎯 Quality Summary:")
        print(f"    Total Tests: {total_qc}")
        print(f"    Passed: {passed_qc}")
        print(f"    Failed: {failed_qc}")
        print(f"    Pass Rate: {pass_rate:.1f}%")
        
        # Inventory Summary
        total_products = len(self.products)
        active_products = len([p for p in self.products if p["is_active"]])
        
        print(f"  📦 Inventory Summary:")
        print(f"    Total Products: {total_products}")
        print(f"    Active Products: {active_products}")
        print(f"    Product Types: {len(set(p['product_type'] for p in self.products))}")
    
    def simulate_real_time_monitoring(self, duration_seconds=30):
        """Simulate real-time monitoring"""
        print(f"\n📊 Real-time monitoring for {duration_seconds} seconds...")
        
        end_time = time.time() + duration_seconds
        update_count = 0
        
        while time.time() < end_time:
            # Simulate monitoring data
            active_batches = len([b for b in self.batches if b["status"] == "IN_PROGRESS"])
            completed_today = len([b for b in self.batches if b["status"] == "COMPLETED" and b["end_date"]])
            efficiency = random.uniform(85, 98)
            
            print(f"  📈 Update {update_count + 1}: {active_batches} active batches, "
                  f"{completed_today} completed today, {efficiency:.1f}% efficiency")
            
            update_count += 1
            time.sleep(5)  # Update every 5 seconds
    
    def run_simulation(self):
        """Run complete production simulation"""
        print("🚀 ChemFactory Production Simulation")
        print("=" * 50)
        print(f"⏰ Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create test data
        self.simulate_product_creation(12)
        self.simulate_manufacturing_orders(6)
        self.simulate_batch_processing(18)
        
        # Generate reports
        self.generate_reports()
        
        # Real-time monitoring
        self.simulate_real_time_monitoring(20)
        
        # Final summary
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print(f"\n🎉 Simulation completed!")
        print(f"⏱️ Duration: {duration:.1f} seconds")
        print(f"📊 Created: {len(self.products)} products, {len(self.manufacturing_orders)} MOs, {len(self.batches)} batches, {len(self.quality_checks)} QC tests")
        
        # Save simulation data
        simulation_data = {
            "products": self.products,
            "manufacturing_orders": self.manufacturing_orders,
            "batches": self.batches,
            "quality_checks": self.quality_checks,
            "simulation_duration": duration,
            "completed_at": end_time.isoformat()
        }
        
        with open('simulation_results.json', 'w') as f:
            json.dump(simulation_data, f, indent=2, default=str)
        
        print(f"💾 Simulation data saved to simulation_results.json")

if __name__ == "__main__":
    simulator = ProductionSimulator()
    simulator.run_simulation()
