"""
AI Model Testing Script for ChemFactory MES/ERP
Tests AI predictions, analytics, and machine learning models
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai.predictive_analytics import PredictiveAnalytics
from workflows.workflow_engine import WorkflowEngine, get_production_approval_workflow, get_quality_control_workflow

class TestPredictiveAnalytics:
    def setup_method(self):
        """Setup test data for AI models"""
        self.analytics = PredictiveAnalytics()
        
        # Generate synthetic batch data for testing
        np.random.seed(42)  # For reproducible results
        self.batch_data = []
        
        for i in range(100):
            batch = {
                'batch_id': i + 1,
                'temperature': np.random.normal(25, 5),
                'pressure': np.random.normal(1.0, 0.2),
                'ph': np.random.normal(7.0, 0.5),
                'mixing_time': np.random.normal(30, 10),
                'quality_score': np.random.normal(85, 10),
                'yield': np.random.normal(95, 5),
                'defect_rate': np.random.exponential(0.02)
            }
            self.batch_data.append(batch)
    
    def test_quality_prediction_training(self):
        """Test quality prediction model training"""
        print("🧠 Testing quality prediction model training...")
        
        # Prepare data
        X, y = self.analytics.prepare_quality_data(self.batch_data)
        
        # Train model
        results = self.analytics.train_quality_model(self.batch_data)
        
        # Verify training results
        assert 'model_accuracy' in results
        assert 'feature_importance' in results
        assert results['model_accuracy'] > 0.7  # Should achieve reasonable accuracy
        assert len(results['feature_importance']) > 0
        
        print(f"  ✅ Model accuracy: {results['model_accuracy']:.2%}")
        print(f"  ✅ Features: {len(results['feature_importance'])}")
    
    def test_quality_prediction(self):
        """Test quality prediction functionality"""
        print("🔮 Testing quality prediction...")
        
        # Train model first
        self.analytics.train_quality_model(self.batch_data)
        
        # Test prediction
        process_params = {
            'temperature': 25.0,
            'pressure': 1.0,
            'ph': 7.0,
            'mixing_time': 30.0
        }
        
        prediction = self.analytics.predict_quality(process_params)
        
        # Verify prediction structure
        assert 'predicted_quality' in prediction
        assert 'confidence' in prediction
        assert 'recommendations' in prediction
        assert 0 <= prediction['predicted_quality'] <= 100
        assert 0 <= prediction['confidence'] <= 1
        
        print(f"  ✅ Predicted quality: {prediction['predicted_quality']:.1f}")
        print(f"  ✅ Confidence: {prediction['confidence']:.2%}")
        print(f"  ✅ Recommendations: {len(prediction['recommendations'])}")
    
    def test_demand_forecasting(self):
        """Test demand forecasting functionality"""
        print("📈 Testing demand forecasting...")
        
        # Generate historical sales data
        historical_data = []
        base_date = datetime.now() - timedelta(days=90)
        
        for i in range(90):
            date = base_date + timedelta(days=i)
            demand = 100 + np.random.normal(0, 20) + 10 * np.sin(i * 2 * np.pi / 7)  # Weekly pattern
            historical_data.append({
                'date': date,
                'demand': max(0, demand)
            })
        
        # Test forecasting
        forecast = self.analytics.predict_demand(historical_data, forecast_days=30)
        
        # Verify forecast structure
        assert 'forecast' in forecast
        assert 'trend' in forecast
        assert 'confidence' in forecast
        assert len(forecast['forecast']) == 30
        
        print(f"  ✅ Forecast period: {len(forecast['forecast'])} days")
        print(f"  ✅ Trend: {forecast['trend']}")
        print(f"  ✅ Confidence: {forecast['confidence']:.2%}")
    
    def test_anomaly_detection(self):
        """Test anomaly detection functionality"""
        print("🚨 Testing anomaly detection...")
        
        # Generate sensor data with some anomalies
        sensor_data = []
        
        # Normal data
        for i in range(80):
            sensor_data.append({
                'timestamp': datetime.now() - timedelta(minutes=80-i),
                'temperature': np.random.normal(25, 2),
                'pressure': np.random.normal(1.0, 0.1),
                'vibration': np.random.normal(0.5, 0.1)
            })
        
        # Add some anomalies
        for i in range(20):
            sensor_data.append({
                'timestamp': datetime.now() - timedelta(minutes=20-i),
                'temperature': np.random.normal(35, 2),  # Higher temperature
                'pressure': np.random.normal(1.5, 0.1),  # Higher pressure
                'vibration': np.random.normal(1.0, 0.1)  # Higher vibration
            })
        
        # Test anomaly detection
        anomalies = self.analytics.detect_anomalies(sensor_data)
        
        # Verify anomaly detection results
        assert 'anomalies' in anomalies
        assert 'anomaly_count' in anomalies
        assert 'severity_distribution' in anomalies
        assert len(anomalies['anomalies']) > 0  # Should detect some anomalies
        
        print(f"  ✅ Anomalies detected: {anomalies['anomaly_count']}")
        print(f"  ✅ Severity distribution: {anomalies['severity_distribution']}")
    
    def test_production_optimization(self):
        """Test production optimization functionality"""
        print("⚙️ Testing production optimization...")
        
        constraints = {
            'max_batches': 10,
            'max_hours': 40,
            'resource_limits': {
                'machine_1': 8,
                'machine_2': 6,
                'machine_3': 4
            },
            'product_demands': {
                'product_a': 100,
                'product_b': 80,
                'product_c': 60
            }
        }
        
        # Test optimization
        optimization = self.analytics.optimize_production_schedule(constraints)
        
        # Verify optimization results
        assert 'schedule' in optimization
        assert 'efficiency' in optimization
        assert 'resource_utilization' in optimization
        assert optimization['efficiency'] > 0
        
        print(f"  ✅ Schedule generated: {len(optimization['schedule'])} items")
        print(f"  ✅ Efficiency: {optimization['efficiency']:.1%}")
        print(f"  ✅ Resource utilization: {optimization['resource_utilization']}")

class TestWorkflowEngine:
    def setup_method(self):
        """Setup workflow engine for testing"""
        # Mock database session
        self.mock_db = None
        self.workflow_engine = WorkflowEngine(self.mock_db)
    
    def test_workflow_definition_creation(self):
        """Test workflow definition creation"""
        print("🔄 Testing workflow definition creation...")
        
        # Test production approval workflow
        prod_workflow = get_production_approval_workflow()
        
        assert 'id' in prod_workflow
        assert 'name' in prod_workflow
        assert 'tasks' in prod_workflow
        assert 'connections' in prod_workflow
        assert len(prod_workflow['tasks']) > 0
        
        print(f"  ✅ Production workflow: {prod_workflow['name']}")
        print(f"  ✅ Tasks: {len(prod_workflow['tasks'])}")
        print(f"  ✅ Connections: {len(prod_workflow['connections'])}")
    
    def test_quality_control_workflow(self):
        """Test quality control workflow"""
        print("🧪 Testing quality control workflow...")
        
        # Test quality control workflow
        qc_workflow = get_quality_control_workflow()
        
        assert 'id' in qc_workflow
        assert 'name' in qc_workflow
        assert 'tasks' in qc_workflow
        assert 'connections' in qc_workflow
        assert len(qc_workflow['tasks']) > 0
        
        print(f"  ✅ QC workflow: {qc_workflow['name']}")
        print(f"  ✅ Tasks: {len(qc_workflow['tasks'])}")
        print(f"  ✅ Connections: {len(qc_workflow['connections'])}")
    
    def test_workflow_engine_initialization(self):
        """Test workflow engine initialization"""
        print("⚙️ Testing workflow engine initialization...")
        
        assert self.workflow_engine.db is not None
        assert isinstance(self.workflow_engine.workflow_definitions, dict)
        assert isinstance(self.workflow_engine.active_instances, dict)
        assert isinstance(self.workflow_engine.task_handlers, dict)
        
        print("  ✅ Workflow engine initialized successfully")

class TestAIIntegration:
    def test_end_to_end_ai_workflow(self):
        """Test complete AI workflow integration"""
        print("🤖 Testing end-to-end AI workflow...")
        
        # Initialize analytics
        analytics = PredictiveAnalytics()
        
        # Generate comprehensive test data
        batch_data = []
        for i in range(50):
            batch = {
                'batch_id': i + 1,
                'temperature': np.random.normal(25, 3),
                'pressure': np.random.normal(1.0, 0.15),
                'ph': np.random.normal(7.0, 0.3),
                'mixing_time': np.random.normal(30, 8),
                'quality_score': np.random.normal(85, 8),
                'yield': np.random.normal(95, 4),
                'defect_rate': np.random.exponential(0.015)
            }
            batch_data.append(batch)
        
        # Train models
        print("  🧠 Training AI models...")
        quality_results = analytics.train_quality_model(batch_data)
        
        # Test predictions
        print("  🔮 Making predictions...")
        process_params = {
            'temperature': 26.0,
            'pressure': 1.1,
            'ph': 7.2,
            'mixing_time': 32.0
        }
        
        quality_prediction = analytics.predict_quality(process_params)
        
        # Test demand forecasting
        print("  📈 Forecasting demand...")
        historical_data = []
        base_date = datetime.now() - timedelta(days=60)
        for i in range(60):
            date = base_date + timedelta(days=i)
            demand = 120 + np.random.normal(0, 15) + 8 * np.sin(i * 2 * np.pi / 7)
            historical_data.append({'date': date, 'demand': max(0, demand)})
        
        demand_forecast = analytics.predict_demand(historical_data, 14)
        
        # Test anomaly detection
        print("  🚨 Detecting anomalies...")
        sensor_data = []
        for i in range(100):
            sensor_data.append({
                'timestamp': datetime.now() - timedelta(minutes=100-i),
                'temperature': np.random.normal(25, 2),
                'pressure': np.random.normal(1.0, 0.1),
                'vibration': np.random.normal(0.5, 0.1)
            })
        
        anomalies = analytics.detect_anomalies(sensor_data)
        
        # Verify all components work together
        assert quality_results['model_accuracy'] > 0.6
        assert quality_prediction['predicted_quality'] > 0
        assert len(demand_forecast['forecast']) == 14
        assert anomalies['anomaly_count'] >= 0
        
        print("  ✅ End-to-end AI workflow completed successfully")
        print(f"    📊 Quality model accuracy: {quality_results['model_accuracy']:.2%}")
        print(f"    🎯 Quality prediction: {quality_prediction['predicted_quality']:.1f}")
        print(f"    📈 Demand forecast: {len(demand_forecast['forecast'])} days")
        print(f"    🚨 Anomalies detected: {anomalies['anomaly_count']}")

def run_ai_tests():
    """Run all AI tests"""
    print("🤖 Starting AI Model Testing Suite")
    print("=" * 50)
    
    # Test Predictive Analytics
    analytics_tests = TestPredictiveAnalytics()
    analytics_tests.setup_method()
    
    try:
        analytics_tests.test_quality_prediction_training()
        analytics_tests.test_quality_prediction()
        analytics_tests.test_demand_forecasting()
        analytics_tests.test_anomaly_detection()
        analytics_tests.test_production_optimization()
        print("✅ All Predictive Analytics tests passed!")
    except Exception as e:
        print(f"❌ Predictive Analytics test failed: {e}")
    
    # Test Workflow Engine
    workflow_tests = TestWorkflowEngine()
    workflow_tests.setup_method()
    
    try:
        workflow_tests.test_workflow_definition_creation()
        workflow_tests.test_quality_control_workflow()
        workflow_tests.test_workflow_engine_initialization()
        print("✅ All Workflow Engine tests passed!")
    except Exception as e:
        print(f"❌ Workflow Engine test failed: {e}")
    
    # Test AI Integration
    integration_tests = TestAIIntegration()
    
    try:
        integration_tests.test_end_to_end_ai_workflow()
        print("✅ All AI Integration tests passed!")
    except Exception as e:
        print(f"❌ AI Integration test failed: {e}")
    
    print("=" * 50)
    print("🎉 AI Testing Suite completed!")

if __name__ == "__main__":
    run_ai_tests()
