from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..db.database import get_db
from ..db.models import (
    Batch, ManufacturingOrder, QualityCheck, Product, 
    InventoryItem, User, JournalEntry, JournalLine
)
from ..core.dependencies import require_viewer, require_admin
import pandas as pd
import numpy as np

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/production/summary")
async def get_production_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get production summary report"""
    
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Production metrics
    total_batches = db.query(Batch).filter(
        Batch.start_date >= start_date,
        Batch.start_date <= end_date
    ).count()
    
    completed_batches = db.query(Batch).filter(
        Batch.status == "COMPLETED",
        Batch.end_date >= start_date,
        Batch.end_date <= end_date
    ).count()
    
    # Calculate efficiency
    efficiency = (completed_batches / total_batches * 100) if total_batches > 0 else 0
    
    # Get top products by production
    top_products = db.query(
        Product.name_en,
        func.count(Batch.id).label('batch_count'),
        func.sum(Batch.actual_quantity).label('total_quantity')
    ).join(Batch).filter(
        Batch.start_date >= start_date,
        Batch.start_date <= end_date,
        Batch.status == "COMPLETED"
    ).group_by(Product.id, Product.name_en).order_by(desc('batch_count')).limit(10).all()
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": {
            "total_batches": total_batches,
            "completed_batches": completed_batches,
            "efficiency": round(efficiency, 2),
            "completion_rate": round(efficiency, 2)
        },
        "top_products": [
            {
                "product_name": product.name_en,
                "batch_count": product.batch_count,
                "total_quantity": float(product.total_quantity) if product.total_quantity else 0
            }
            for product in top_products
        ]
    }

@router.get("/quality/trends")
async def get_quality_trends(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get quality trends report"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Daily quality metrics
    daily_quality = db.query(
        func.date(QualityCheck.tested_at).label('date'),
        func.count(QualityCheck.id).label('total_tests'),
        func.sum(func.case([(QualityCheck.status == "PASS", 1)], else_=0)).label('passed_tests')
    ).filter(
        QualityCheck.tested_at >= start_date,
        QualityCheck.tested_at <= end_date
    ).group_by(func.date(QualityCheck.tested_at)).order_by('date').all()
    
    # Calculate pass rates
    trends = []
    for day in daily_quality:
        pass_rate = (day.passed_tests / day.total_tests * 100) if day.total_tests > 0 else 0
        trends.append({
            "date": day.date.isoformat(),
            "total_tests": day.total_tests,
            "passed_tests": day.passed_tests,
            "pass_rate": round(pass_rate, 2)
        })
    
    # Overall quality metrics
    total_tests = sum(trend['total_tests'] for trend in trends)
    total_passed = sum(trend['passed_tests'] for trend in trends)
    overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    return {
        "period_days": days,
        "overall_metrics": {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "overall_pass_rate": round(overall_pass_rate, 2)
        },
        "daily_trends": trends
    }

@router.get("/inventory/analysis")
async def get_inventory_analysis(
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get inventory analysis report"""
    
    # Inventory summary
    total_items = db.query(InventoryItem).count()
    low_stock_items = db.query(InventoryItem).filter(
        InventoryItem.quantity <= InventoryItem.min_quantity
    ).count()
    
    # Calculate total inventory value
    inventory_value = db.query(
        func.sum(InventoryItem.quantity * InventoryItem.unit_cost)
    ).scalar() or 0
    
    # ABC Analysis (simplified)
    items_with_value = db.query(
        InventoryItem,
        (InventoryItem.quantity * InventoryItem.unit_cost).label('total_value')
    ).order_by(desc('total_value')).all()
    
    total_value = sum(item.total_value for item in items_with_value)
    
    abc_analysis = []
    cumulative_value = 0
    
    for item in items_with_value:
        cumulative_value += item.total_value
        percentage = (cumulative_value / total_value * 100) if total_value > 0 else 0
        
        category = "A" if percentage <= 80 else "B" if percentage <= 95 else "C"
        
        abc_analysis.append({
            "product_name": item.InventoryItem.product.name_en,
            "quantity": item.InventoryItem.quantity,
            "unit_cost": float(item.InventoryItem.unit_cost),
            "total_value": float(item.total_value),
            "percentage": round(percentage, 2),
            "category": category
        })
    
    return {
        "summary": {
            "total_items": total_items,
            "low_stock_items": low_stock_items,
            "total_value": round(float(inventory_value), 2),
            "low_stock_percentage": round((low_stock_items / total_items * 100) if total_items > 0 else 0, 2)
        },
        "abc_analysis": abc_analysis[:20]  # Top 20 items
    }

@router.get("/financial/summary")
async def get_financial_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Get financial summary report"""
    
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Revenue from completed batches
    revenue = db.query(
        func.sum(Batch.actual_quantity * Product.unit_price)
    ).join(Product).filter(
        Batch.status == "COMPLETED",
        Batch.end_date >= start_date,
        Batch.end_date <= end_date
    ).scalar() or 0
    
    # Cost analysis
    material_costs = db.query(
        func.sum(JournalLine.debit)
    ).join(JournalEntry).filter(
        JournalEntry.description.like('%Material%'),
        JournalEntry.date >= start_date,
        JournalEntry.date <= end_date
    ).scalar() or 0
    
    labor_costs = db.query(
        func.sum(JournalLine.debit)
    ).join(JournalEntry).filter(
        JournalEntry.description.like('%Labor%'),
        JournalEntry.date >= start_date,
        JournalEntry.date <= end_date
    ).scalar() or 0
    
    overhead_costs = db.query(
        func.sum(JournalLine.debit)
    ).join(JournalEntry).filter(
        JournalEntry.description.like('%Overhead%'),
        JournalEntry.date >= start_date,
        JournalEntry.date <= end_date
    ).scalar() or 0
    
    total_costs = material_costs + labor_costs + overhead_costs
    gross_profit = revenue - total_costs
    profit_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "revenue": {
            "total_revenue": round(float(revenue), 2),
            "revenue_per_day": round(float(revenue) / (end_date - start_date).days, 2)
        },
        "costs": {
            "material_costs": round(float(material_costs), 2),
            "labor_costs": round(float(labor_costs), 2),
            "overhead_costs": round(float(overhead_costs), 2),
            "total_costs": round(float(total_costs), 2)
        },
        "profitability": {
            "gross_profit": round(float(gross_profit), 2),
            "profit_margin": round(profit_margin, 2)
        }
    }

@router.get("/efficiency/analysis")
async def get_efficiency_analysis(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get efficiency analysis report"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Production efficiency
    batches = db.query(Batch).filter(
        Batch.start_date >= start_date,
        Batch.start_date <= end_date,
        Batch.status == "COMPLETED"
    ).all()
    
    if not batches:
        return {"message": "No completed batches in the specified period"}
    
    # Calculate efficiency metrics
    total_planned_time = sum(
        (batch.planned_end_date - batch.planned_start_date).total_seconds() / 3600
        for batch in batches if batch.planned_start_date and batch.planned_end_date
    )
    
    total_actual_time = sum(
        (batch.end_date - batch.start_date).total_seconds() / 3600
        for batch in batches if batch.start_date and batch.end_date
    )
    
    time_efficiency = (total_planned_time / total_actual_time * 100) if total_actual_time > 0 else 0
    
    # Quantity efficiency
    total_planned_qty = sum(batch.target_quantity for batch in batches)
    total_actual_qty = sum(batch.actual_quantity for batch in batches if batch.actual_quantity)
    quantity_efficiency = (total_actual_qty / total_planned_qty * 100) if total_planned_qty > 0 else 0
    
    # Quality efficiency
    quality_efficiency = 95.0  # This would be calculated from quality data
    
    return {
        "period_days": days,
        "efficiency_metrics": {
            "time_efficiency": round(time_efficiency, 2),
            "quantity_efficiency": round(quantity_efficiency, 2),
            "quality_efficiency": round(quality_efficiency, 2),
            "overall_efficiency": round((time_efficiency + quantity_efficiency + quality_efficiency) / 3, 2)
        },
        "production_data": {
            "total_batches": len(batches),
            "total_planned_time_hours": round(total_planned_time, 2),
            "total_actual_time_hours": round(total_actual_time, 2),
            "total_planned_quantity": round(total_planned_qty, 2),
            "total_actual_quantity": round(total_actual_qty, 2)
        }
    }

@router.get("/kpi/dashboard")
async def get_kpi_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get KPI dashboard with key performance indicators"""
    
    # Production KPIs
    active_batches = db.query(Batch).filter(Batch.status == "IN_PROGRESS").count()
    completed_today = db.query(Batch).filter(
        Batch.status == "COMPLETED",
        Batch.end_date >= datetime.utcnow().date()
    ).count()
    
    # Quality KPIs
    total_qc = db.query(QualityCheck).count()
    passed_qc = db.query(QualityCheck).filter(QualityCheck.status == "PASS").count()
    quality_pass_rate = (passed_qc / total_qc * 100) if total_qc > 0 else 0
    
    # Inventory KPIs
    low_stock_items = db.query(InventoryItem).filter(
        InventoryItem.quantity <= InventoryItem.min_quantity
    ).count()
    
    # Efficiency KPIs
    overall_efficiency = 92.5  # This would be calculated from various metrics
    
    return {
        "production_kpis": {
            "active_batches": active_batches,
            "completed_today": completed_today,
            "production_efficiency": round(overall_efficiency, 2)
        },
        "quality_kpis": {
            "pass_rate": round(quality_pass_rate, 2),
            "total_tests": total_qc,
            "quality_score": round(quality_pass_rate, 2)
        },
        "inventory_kpis": {
            "low_stock_items": low_stock_items,
            "inventory_turnover": 8.5,  # This would be calculated
            "stock_accuracy": 98.2  # This would be calculated
        },
        "financial_kpis": {
            "revenue_today": 15000.0,  # This would be calculated
            "cost_per_unit": 12.50,  # This would be calculated
            "profit_margin": 15.8  # This would be calculated
        },
        "timestamp": datetime.utcnow().isoformat()
    }
