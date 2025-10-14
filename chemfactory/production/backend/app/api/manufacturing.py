from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..db.database import get_db
from ..db.models import ManufacturingOrder, Product, BOM, User
from ..db.schemas import ManufacturingOrder as MOSchema, ManufacturingOrderCreate, ManufacturingOrderUpdate
from ..core.dependencies import require_production_manager, require_operator, require_viewer

router = APIRouter(prefix="/manufacturing", tags=["manufacturing"])

@router.get("/orders", response_model=List[MOSchema])
def get_manufacturing_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    product_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get all manufacturing orders with filtering"""
    query = db.query(ManufacturingOrder)
    
    if status:
        query = query.filter(ManufacturingOrder.status == status)
    
    if product_id:
        query = query.filter(ManufacturingOrder.product_id == product_id)
    
    if start_date:
        query = query.filter(ManufacturingOrder.planned_start_date >= start_date)
    
    if end_date:
        query = query.filter(ManufacturingOrder.planned_end_date <= end_date)
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@router.get("/orders/{order_id}", response_model=MOSchema)
def get_manufacturing_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get a specific manufacturing order by ID"""
    order = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturing order not found"
        )
    return order

@router.post("/orders", response_model=MOSchema)
def create_manufacturing_order(
    order: ManufacturingOrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_production_manager)
):
    """Create a new manufacturing order"""
    # Validate product exists
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product not found"
        )
    
    # Validate BOM exists
    bom = db.query(BOM).filter(BOM.id == order.bom_id).first()
    if not bom:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="BOM not found"
        )
    
    # Generate MO number
    mo_number = f"MO{datetime.now().strftime('%Y%m%d')}{db.query(ManufacturingOrder).count() + 1:04d}"
    
    db_order = ManufacturingOrder(
        mo_number=mo_number,
        bom_id=order.bom_id,
        product_id=order.product_id,
        target_quantity=order.target_quantity,
        planned_start_date=order.planned_start_date,
        planned_end_date=order.planned_end_date,
        priority=order.priority,
        created_by_id=current_user.id,
        status="PLANNED"
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.put("/orders/{order_id}", response_model=MOSchema)
def update_manufacturing_order(
    order_id: int,
    order_update: ManufacturingOrderUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_production_manager)
):
    """Update a manufacturing order"""
    db_order = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == order_id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturing order not found"
        )
    
    # Update fields
    update_data = order_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order, field, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.post("/orders/{order_id}/start")
def start_manufacturing_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator)
):
    """Start a manufacturing order"""
    order = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturing order not found"
        )
    
    if order.status != "PLANNED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order can only be started from PLANNED status"
        )
    
    order.status = "IN_PROGRESS"
    order.actual_start_date = datetime.utcnow()
    db.commit()
    
    return {"message": "Manufacturing order started successfully"}

@router.post("/orders/{order_id}/complete")
def complete_manufacturing_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator)
):
    """Complete a manufacturing order"""
    order = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturing order not found"
        )
    
    if order.status != "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be in progress to complete"
        )
    
    order.status = "COMPLETED"
    order.actual_end_date = datetime.utcnow()
    db.commit()
    
    return {"message": "Manufacturing order completed successfully"}

@router.post("/orders/{order_id}/cancel")
def cancel_manufacturing_order(
    order_id: int,
    reason: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_production_manager)
):
    """Cancel a manufacturing order"""
    order = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturing order not found"
        )
    
    if order.status in ["COMPLETED", "CANCELLED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be cancelled"
        )
    
    order.status = "CANCELLED"
    db.commit()
    
    return {"message": "Manufacturing order cancelled successfully"}

@router.get("/orders/{order_id}/status")
def get_order_status(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get manufacturing order status and progress"""
    order = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturing order not found"
        )
    
    # Calculate progress based on status
    progress = 0
    if order.status == "PLANNED":
        progress = 0
    elif order.status == "IN_PROGRESS":
        if order.actual_start_date:
            total_duration = (order.planned_end_date - order.planned_start_date).total_seconds()
            elapsed = (datetime.utcnow() - order.actual_start_date).total_seconds()
            progress = min(90, (elapsed / total_duration) * 100) if total_duration > 0 else 0
    elif order.status == "COMPLETED":
        progress = 100
    
    return {
        "order_id": order_id,
        "status": order.status,
        "progress": round(progress, 2),
        "planned_start": order.planned_start_date.isoformat() if order.planned_start_date else None,
        "planned_end": order.planned_end_date.isoformat() if order.planned_end_date else None,
        "actual_start": order.actual_start_date.isoformat() if order.actual_start_date else None,
        "actual_end": order.actual_end_date.isoformat() if order.actual_end_date else None
    }

@router.get("/dashboard/stats")
def get_manufacturing_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get manufacturing dashboard statistics"""
    total_orders = db.query(ManufacturingOrder).count()
    active_orders = db.query(ManufacturingOrder).filter(ManufacturingOrder.status == "IN_PROGRESS").count()
    completed_orders = db.query(ManufacturingOrder).filter(ManufacturingOrder.status == "COMPLETED").count()
    planned_orders = db.query(ManufacturingOrder).filter(ManufacturingOrder.status == "PLANNED").count()
    
    # Calculate completion rate
    completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
    
    return {
        "total_orders": total_orders,
        "active_orders": active_orders,
        "completed_orders": completed_orders,
        "planned_orders": planned_orders,
        "completion_rate": round(completion_rate, 2)
    }
