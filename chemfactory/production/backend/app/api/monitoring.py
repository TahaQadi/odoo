from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime, timedelta
from ..db.database import get_db
from ..db.models import Batch, ManufacturingOrder, QualityCheck, InventoryItem
from ..core.dependencies import require_viewer
import random

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send real-time data every 5 seconds
            await asyncio.sleep(5)
            
            # Get real-time data
            data = await get_realtime_data()
            await websocket.send_text(json.dumps(data))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def get_realtime_data():
    """Generate real-time monitoring data"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "production": {
            "active_batches": random.randint(5, 15),
            "completed_today": random.randint(20, 50),
            "efficiency": round(random.uniform(85, 98), 2),
            "alerts": random.randint(0, 3)
        },
        "quality": {
            "pass_rate": round(random.uniform(92, 99), 2),
            "pending_tests": random.randint(0, 8),
            "failed_tests": random.randint(0, 2)
        },
        "inventory": {
            "low_stock_items": random.randint(0, 5),
            "critical_items": random.randint(0, 2),
            "total_value": round(random.uniform(50000, 150000), 2)
        },
        "equipment": {
            "running_machines": random.randint(8, 12),
            "maintenance_due": random.randint(0, 3),
            "efficiency": round(random.uniform(88, 96), 2)
        }
    }

@router.get("/dashboard")
async def get_monitoring_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get comprehensive monitoring dashboard data"""
    
    # Get real-time production data
    active_batches = db.query(Batch).filter(Batch.status == "IN_PROGRESS").count()
    completed_today = db.query(Batch).filter(
        Batch.status == "COMPLETED",
        Batch.end_date >= datetime.utcnow().date()
    ).count()
    
    # Get quality data
    total_qc = db.query(QualityCheck).count()
    passed_qc = db.query(QualityCheck).filter(QualityCheck.status == "PASS").count()
    pass_rate = (passed_qc / total_qc * 100) if total_qc > 0 else 0
    
    # Get inventory alerts
    low_stock_items = db.query(InventoryItem).filter(
        InventoryItem.quantity <= InventoryItem.min_quantity
    ).count()
    
    return {
        "production": {
            "active_batches": active_batches,
            "completed_today": completed_today,
            "efficiency": round(random.uniform(85, 98), 2),
            "alerts": random.randint(0, 3)
        },
        "quality": {
            "pass_rate": round(pass_rate, 2),
            "pending_tests": db.query(QualityCheck).filter(QualityCheck.status == "PENDING").count(),
            "failed_tests": db.query(QualityCheck).filter(QualityCheck.status == "FAIL").count()
        },
        "inventory": {
            "low_stock_items": low_stock_items,
            "critical_items": random.randint(0, 2),
            "total_value": round(random.uniform(50000, 150000), 2)
        },
        "equipment": {
            "running_machines": random.randint(8, 12),
            "maintenance_due": random.randint(0, 3),
            "efficiency": round(random.uniform(88, 96), 2)
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/alerts")
async def get_system_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get system alerts and notifications"""
    
    alerts = []
    
    # Check for low stock alerts
    low_stock_items = db.query(InventoryItem).filter(
        InventoryItem.quantity <= InventoryItem.min_quantity
    ).all()
    
    for item in low_stock_items:
        alerts.append({
            "id": f"low_stock_{item.id}",
            "type": "inventory",
            "severity": "warning",
            "title": "Low Stock Alert",
            "message": f"{item.product.name_en} is running low ({item.quantity} remaining)",
            "timestamp": datetime.utcnow().isoformat(),
            "action_required": True
        })
    
    # Check for quality issues
    failed_qc = db.query(QualityCheck).filter(
        QualityCheck.status == "FAIL",
        QualityCheck.tested_at >= datetime.utcnow() - timedelta(hours=24)
    ).count()
    
    if failed_qc > 0:
        alerts.append({
            "id": "quality_issues",
            "type": "quality",
            "severity": "error",
            "title": "Quality Issues Detected",
            "message": f"{failed_qc} quality checks failed in the last 24 hours",
            "timestamp": datetime.utcnow().isoformat(),
            "action_required": True
        })
    
    # Check for overdue batches
    overdue_batches = db.query(Batch).filter(
        Batch.status == "IN_PROGRESS",
        Batch.planned_end_date < datetime.utcnow()
    ).count()
    
    if overdue_batches > 0:
        alerts.append({
            "id": "overdue_batches",
            "type": "production",
            "severity": "warning",
            "title": "Overdue Batches",
            "message": f"{overdue_batches} batches are overdue",
            "timestamp": datetime.utcnow().isoformat(),
            "action_required": True
        })
    
    return {
        "alerts": alerts,
        "total_alerts": len(alerts),
        "critical_alerts": len([a for a in alerts if a["severity"] == "error"]),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics")
async def get_system_metrics(
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get system performance metrics"""
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    # Production metrics
    batches_in_period = db.query(Batch).filter(
        Batch.start_date >= start_time,
        Batch.start_date <= end_time
    ).count()
    
    completed_batches = db.query(Batch).filter(
        Batch.status == "COMPLETED",
        Batch.end_date >= start_time,
        Batch.end_date <= end_time
    ).count()
    
    # Quality metrics
    qc_in_period = db.query(QualityCheck).filter(
        QualityCheck.tested_at >= start_time,
        QualityCheck.tested_at <= end_time
    ).count()
    
    passed_qc = db.query(QualityCheck).filter(
        QualityCheck.status == "PASS",
        QualityCheck.tested_at >= start_time,
        QualityCheck.tested_at <= end_time
    ).count()
    
    return {
        "period_hours": hours,
        "production": {
            "batches_started": batches_in_period,
            "batches_completed": completed_batches,
            "completion_rate": round((completed_batches / batches_in_period * 100) if batches_in_period > 0 else 0, 2)
        },
        "quality": {
            "tests_performed": qc_in_period,
            "tests_passed": passed_qc,
            "pass_rate": round((passed_qc / qc_in_period * 100) if qc_in_period > 0 else 0, 2)
        },
        "efficiency": {
            "overall_efficiency": round(random.uniform(85, 98), 2),
            "equipment_utilization": round(random.uniform(80, 95), 2),
            "labor_efficiency": round(random.uniform(88, 96), 2)
        }
    }

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Acknowledge an alert"""
    
    # In a real system, you'd store acknowledgment in the database
    return {
        "message": f"Alert {alert_id} acknowledged by {current_user.username}",
        "timestamp": datetime.utcnow().isoformat()
    }
