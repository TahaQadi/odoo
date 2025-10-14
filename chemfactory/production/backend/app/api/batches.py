from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..db.database import get_db
from ..db.models import Batch, Product, ManufacturingOrder, User, BatchStatus
from ..db.schemas import Batch as BatchSchema, BatchCreate, BatchUpdate
from ..core.dependencies import require_operator, require_production_manager, require_viewer

router = APIRouter(prefix="/batches", tags=["batches"])

@router.get("/", response_model=List[BatchSchema])
def get_batches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[BatchStatus] = None,
    product_id: Optional[int] = None,
    manufacturing_order_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get all batches with filtering"""
    query = db.query(Batch)
    
    if status:
        query = query.filter(Batch.status == status)
    
    if product_id:
        query = query.filter(Batch.product_id == product_id)
    
    if manufacturing_order_id:
        query = query.filter(Batch.manufacturing_order_id == manufacturing_order_id)
    
    if start_date:
        query = query.filter(Batch.start_date >= start_date)
    
    if end_date:
        query = query.filter(Batch.end_date <= end_date)
    
    batches = query.offset(skip).limit(limit).all()
    return batches

@router.get("/{batch_id}", response_model=BatchSchema)
def get_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get a specific batch by ID"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    return batch

@router.post("/", response_model=BatchSchema)
def create_batch(
    batch: BatchCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator)
):
    """Create a new batch"""
    # Validate product exists
    product = db.query(Product).filter(Product.id == batch.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product not found"
        )
    
    # Validate manufacturing order exists if provided
    if batch.manufacturing_order_id:
        mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == batch.manufacturing_order_id).first()
        if not mo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manufacturing order not found"
            )
    
    # Generate batch number
    batch_number = f"B{datetime.now().strftime('%Y%m%d')}{db.query(Batch).count() + 1:04d}"
    
    db_batch = Batch(
        batch_number=batch_number,
        product_id=batch.product_id,
        manufacturing_order_id=batch.manufacturing_order_id,
        target_quantity=batch.target_quantity,
        actual_quantity=batch.actual_quantity,
        start_date=batch.start_date,
        end_date=batch.end_date,
        status=batch.status,
        operator_id=batch.operator_id,
        created_by_id=current_user.id
    )
    
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch

@router.put("/{batch_id}", response_model=BatchSchema)
def update_batch(
    batch_id: int,
    batch_update: BatchUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator)
):
    """Update a batch"""
    db_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Update fields
    update_data = batch_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_batch, field, value)
    
    db.commit()
    db.refresh(db_batch)
    return db_batch

@router.post("/{batch_id}/start")
def start_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator)
):
    """Start a batch"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    if batch.status != BatchStatus.PLANNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch can only be started from PLANNED status"
        )
    
    batch.status = BatchStatus.IN_PROGRESS
    batch.start_date = datetime.utcnow()
    batch.operator_id = current_user.id
    db.commit()
    
    return {"message": "Batch started successfully"}

@router.post("/{batch_id}/complete")
def complete_batch(
    batch_id: int,
    actual_quantity: float,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator)
):
    """Complete a batch"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    if batch.status != BatchStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch must be in progress to complete"
        )
    
    batch.status = BatchStatus.COMPLETED
    batch.actual_quantity = actual_quantity
    batch.end_date = datetime.utcnow()
    db.commit()
    
    return {"message": "Batch completed successfully"}

@router.post("/{batch_id}/hold")
def hold_batch(
    batch_id: int,
    reason: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_production_manager)
):
    """Put a batch on hold"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    if batch.status not in [BatchStatus.PLANNED, BatchStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch cannot be put on hold"
        )
    
    batch.status = BatchStatus.ON_HOLD
    db.commit()
    
    return {"message": "Batch put on hold successfully"}

@router.post("/{batch_id}/cancel")
def cancel_batch(
    batch_id: int,
    reason: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_production_manager)
):
    """Cancel a batch"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    if batch.status in [BatchStatus.COMPLETED, BatchStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch cannot be cancelled"
        )
    
    batch.status = BatchStatus.CANCELLED
    db.commit()
    
    return {"message": "Batch cancelled successfully"}

@router.get("/{batch_id}/status")
def get_batch_status(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get batch status and progress"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Calculate progress based on status
    progress = 0
    if batch.status == BatchStatus.PLANNED:
        progress = 0
    elif batch.status == BatchStatus.IN_PROGRESS:
        if batch.start_date:
            # Estimate progress based on time elapsed
            if batch.manufacturing_order and batch.manufacturing_order.planned_end_date:
                total_duration = (batch.manufacturing_order.planned_end_date - batch.manufacturing_order.planned_start_date).total_seconds()
                elapsed = (datetime.utcnow() - batch.start_date).total_seconds()
                progress = min(90, (elapsed / total_duration) * 100) if total_duration > 0 else 50
            else:
                progress = 50
    elif batch.status == BatchStatus.COMPLETED:
        progress = 100
    
    return {
        "batch_id": batch_id,
        "batch_number": batch.batch_number,
        "status": batch.status.value,
        "progress": round(progress, 2),
        "target_quantity": batch.target_quantity,
        "actual_quantity": batch.actual_quantity,
        "start_date": batch.start_date.isoformat() if batch.start_date else None,
        "end_date": batch.end_date.isoformat() if batch.end_date else None
    }

@router.get("/dashboard/stats")
def get_batch_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get batch dashboard statistics"""
    total_batches = db.query(Batch).count()
    active_batches = db.query(Batch).filter(Batch.status == BatchStatus.IN_PROGRESS).count()
    completed_batches = db.query(Batch).filter(Batch.status == BatchStatus.COMPLETED).count()
    planned_batches = db.query(Batch).filter(Batch.status == BatchStatus.PLANNED).count()
    on_hold_batches = db.query(Batch).filter(Batch.status == BatchStatus.ON_HOLD).count()
    
    # Calculate completion rate
    completion_rate = (completed_batches / total_batches * 100) if total_batches > 0 else 0
    
    # Calculate efficiency (actual vs target quantity)
    completed_batches_with_qty = db.query(Batch).filter(
        Batch.status == BatchStatus.COMPLETED,
        Batch.actual_quantity.isnot(None),
        Batch.target_quantity > 0
    ).all()
    
    efficiency = 0
    if completed_batches_with_qty:
        total_efficiency = sum(
            (batch.actual_quantity / batch.target_quantity) * 100 
            for batch in completed_batches_with_qty
        )
        efficiency = total_efficiency / len(completed_batches_with_qty)
    
    return {
        "total_batches": total_batches,
        "active_batches": active_batches,
        "completed_batches": completed_batches,
        "planned_batches": planned_batches,
        "on_hold_batches": on_hold_batches,
        "completion_rate": round(completion_rate, 2),
        "efficiency": round(efficiency, 2)
    }
