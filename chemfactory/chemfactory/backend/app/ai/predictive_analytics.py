"""
Predictive Analytics Engine for ChemFactory MES/ERP
Provides AI-powered insights for manufacturing optimization
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional, Tuple
import joblib
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PredictiveAnalytics:
    """AI-powered predictive analytics for manufacturing optimization"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.is_trained = False
    
    def prepare_quality_data(self, batch_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for quality prediction model"""
        features = []
        targets = []
        
        for batch in batch_data:
            # Extract features
            feature_vector = [
                batch.get('temperature', 0),
                batch.get('pressure', 0),
                batch.get('ph_level', 7),
                batch.get('mixing_time', 0),
                batch.get('ingredient_ratio', 0),
                batch.get('operator_experience', 0),
                batch.get('equipment_age', 0),
                batch.get('ambient_humidity', 50),
                batch.get('ambient_temperature', 25)
            ]
            features.append(feature_vector)
            
            # Extract target (quality score)
            quality_score = batch.get('quality_score', 0)
            targets.append(quality_score)
        
        return np.array(features), np.array(targets)
    
    def train_quality_model(self, batch_data: List[Dict]) -> Dict:
        """Train quality prediction model"""
        try:
            X, y = self.prepare_quality_data(batch_data)
            
            if len(X) < 10:
                return {"error": "Insufficient data for training"}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            
            # Store model and scaler
            self.models['quality_prediction'] = model
            self.scalers['quality_prediction'] = scaler
            self.is_trained = True
            
            return {
                "status": "success",
                "train_score": train_score,
                "test_score": test_score,
                "feature_importance": model.feature_importances_.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error training quality model: {e}")
            return {"error": str(e)}
    
    def predict_quality(self, process_params: Dict) -> Dict:
        """Predict quality score for given process parameters"""
        if not self.is_trained:
            return {"error": "Model not trained"}
        
        try:
            # Prepare input features
            features = np.array([[
                process_params.get('temperature', 0),
                process_params.get('pressure', 0),
                process_params.get('ph_level', 7),
                process_params.get('mixing_time', 0),
                process_params.get('ingredient_ratio', 0),
                process_params.get('operator_experience', 0),
                process_params.get('equipment_age', 0),
                process_params.get('ambient_humidity', 50),
                process_params.get('ambient_temperature', 25)
            ]])
            
            # Scale features
            scaler = self.scalers['quality_prediction']
            features_scaled = scaler.transform(features)
            
            # Make prediction
            model = self.models['quality_prediction']
            prediction = model.predict(features_scaled)[0]
            
            # Calculate confidence
            confidence = min(95, max(60, 100 - abs(prediction - 85) * 2))
            
            return {
                "predicted_quality": round(prediction, 2),
                "confidence": round(confidence, 1),
                "recommendations": self._get_quality_recommendations(prediction, process_params)
            }
            
        except Exception as e:
            logger.error(f"Error predicting quality: {e}")
            return {"error": str(e)}
    
    def _get_quality_recommendations(self, prediction: float, params: Dict) -> List[str]:
        """Generate recommendations based on quality prediction"""
        recommendations = []
        
        if prediction < 70:
            recommendations.append("Consider adjusting temperature settings")
            recommendations.append("Check ingredient ratios")
            recommendations.append("Verify equipment calibration")
        elif prediction < 85:
            recommendations.append("Fine-tune mixing time")
            recommendations.append("Monitor environmental conditions")
        else:
            recommendations.append("Excellent process parameters")
            recommendations.append("Consider documenting as standard")
        
        return recommendations
    
    def predict_demand(self, historical_data: List[Dict], forecast_days: int = 30) -> Dict:
        """Predict future demand using time series analysis"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            
            # Simple moving average forecast
            window = min(7, len(df) // 2)
            forecast = df['demand'].rolling(window=window).mean().iloc[-1]
            
            # Generate forecast for next 30 days
            forecast_dates = pd.date_range(
                start=df.index[-1] + timedelta(days=1),
                periods=forecast_days,
                freq='D'
            )
            
            forecast_values = [forecast] * forecast_days
            
            return {
                "forecast": [
                    {"date": date.strftime("%Y-%m-%d"), "demand": round(value, 2)}
                    for date, value in zip(forecast_dates, forecast_values)
                ],
                "trend": "stable",  # Could be enhanced with trend analysis
                "confidence": 75.0
            }
            
        except Exception as e:
            logger.error(f"Error predicting demand: {e}")
            return {"error": str(e)}
    
    def detect_anomalies(self, sensor_data: List[Dict]) -> Dict:
        """Detect anomalies in real-time sensor data"""
        try:
            if len(sensor_data) < 10:
                return {"anomalies": [], "status": "insufficient_data"}
            
            # Extract sensor values
            values = [point['value'] for point in sensor_data]
            
            # Simple statistical anomaly detection
            mean_val = np.mean(values)
            std_val = np.std(values)
            threshold = 2 * std_val
            
            anomalies = []
            for i, point in enumerate(sensor_data):
                if abs(point['value'] - mean_val) > threshold:
                    anomalies.append({
                        "timestamp": point['timestamp'],
                        "value": point['value'],
                        "severity": "high" if abs(point['value'] - mean_val) > 3 * std_val else "medium",
                        "description": f"Value {point['value']} deviates significantly from mean {mean_val:.2f}"
                    })
            
            return {
                "anomalies": anomalies,
                "status": "success",
                "total_anomalies": len(anomalies)
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return {"error": str(e)}
    
    def optimize_production_schedule(self, constraints: Dict) -> Dict:
        """Optimize production schedule using AI"""
        try:
            # Simple optimization algorithm
            # In production, this would use more sophisticated optimization
            
            products = constraints.get('products', [])
            demand = constraints.get('demand', {})
            resources = constraints.get('resources', {})
            
            optimized_schedule = []
            
            for product in products:
                product_demand = demand.get(product['id'], 0)
                production_capacity = resources.get('daily_capacity', 1000)
                
                # Calculate optimal production quantity
                optimal_quantity = min(product_demand, production_capacity)
                
                # Calculate production time
                production_time = optimal_quantity * product.get('time_per_unit', 1)
                
                optimized_schedule.append({
                    "product_id": product['id'],
                    "quantity": optimal_quantity,
                    "production_time": production_time,
                    "efficiency": min(100, (optimal_quantity / production_capacity) * 100)
                })
            
            return {
                "schedule": optimized_schedule,
                "total_efficiency": sum(item['efficiency'] for item in optimized_schedule) / len(optimized_schedule),
                "recommendations": [
                    "Consider batch production for similar products",
                    "Optimize changeover times between products",
                    "Monitor equipment utilization rates"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing schedule: {e}")
            return {"error": str(e)}
    
    def save_models(self, filepath: str):
        """Save trained models to disk"""
        if self.is_trained:
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'is_trained': self.is_trained
            }
            joblib.dump(model_data, filepath)
    
    def load_models(self, filepath: str):
        """Load trained models from disk"""
        try:
            model_data = joblib.load(filepath)
            self.models = model_data['models']
            self.scalers = model_data['scalers']
            self.is_trained = model_data['is_trained']
        except Exception as e:
            logger.error(f"Error loading models: {e}")
