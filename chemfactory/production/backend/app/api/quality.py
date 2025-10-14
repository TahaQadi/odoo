from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..db.database import get_db
from ..db.models import QualityCheck, Batch, User, QCStatus
from ..db.schemas import QualityCheck as QCSchema, QualityCheckCreate, QualityCheckUpdate
from ..core.dependencies import require_qa, require_operator, require_viewer

router = APIRouter(prefix="/quality", tags=["quality"])

@router.get("/checks", response_model=List[QCSchema])
def get_quality_checks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[QCStatus] = None,
    batch_id: Optional[int] = None,
    tested_by_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get all quality checks with filtering"""
    query = db.query(QualityCheck)
    
    if status:
        query = query.filter(QualityCheck.status == status)
    
    if batch_id:
        query = query.filter(QualityCheck.batch_id == batch_id)
    
    if tested_by_id:
        query = query.filter(QualityCheck.tested_by_id == tested_by_id)
    
    if start_date:
        query = query.filter(QualityCheck.tested_at >= start_date)
    
    if end_date:
        query = query.filter(QualityCheck.tested_at <= end_date)
    
    checks = query.offset(skip).limit(limit).all()
    return checks

@router.get("/checks/{check_id}", response_model=QCSchema)
def get_quality_check(
    check_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get a specific quality check by ID"""
    check = db.query(QualityCheck).filter(QualityCheck.id == check_id).first()
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quality check not found"
        )
    return check

@router.post("/checks", response_model=QCSchema)
def create_quality_check(
    check: QualityCheckCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_qa)
):
    """Create a new quality check"""
    # Validate batch exists
    batch = db.query(Batch).filter(Batch.id == check.batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch not found"
        )
    
    db_check = QualityCheck(
        batch_id=check.batch_id,
        test_name_en=check.test_name_en,
        test_name_ar=check.test_name_ar,
        test_method=check.test_method,
        target_value=check.target_value,
        tolerance_min=check.tolerance_min,
        tolerance_max=check.tolerance_max,
        actual_value=check.actual_value,
        unit=check.unit,
        status=check.status,
        tested_by_id=check.tested_by_id,
        tested_at=check.tested_at,
        notes=check.notes
    )
    
    db.add(db_check)
    db.commit()
    db.refresh(db_check)
    return db_check

@router.put("/checks/{check_id}", response_model=QCSchema)
def update_quality_check(
    check_id: int,
    check_update: QualityCheckUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_qa)
):
    """Update a quality check"""
    db_check = db.query(QualityCheck).filter(QualityCheck.id == check_id).first()
    if not db_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quality check not found"
        )
    
    # Update fields
    update_data = check_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_check, field, value)
    
    db.commit()
    db.refresh(db_check)
    return db_check

@router.post("/checks/{check_id}/test")
def perform_quality_test(
    check_id: int,
    actual_value: float,
    notes: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_qa)
):
    """Perform a quality test and record results"""
    check = db.query(QualityCheck).filter(QualityCheck.id == check_id).first()
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quality check not found"
        )
    
    if check.status != QCStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quality check is not pending"
        )
    
    # Update test results
    check.actual_value = actual_value
    check.tested_by_id = current_user.id
    check.tested_at = datetime.utcnow()
    check.notes = notes
    
    # Determine pass/fail based on tolerances
    if check.target_value and check.tolerance_min is not None and check.tolerance_max is not None:
        min_value = check.target_value - check.tolerance_min
        max_value = check.target_value + check.tolerance_max
        
        if min_value <= actual_value <= max_value:
            check.status = QCStatus.PASS
        else:
            check.status = QCStatus.FAIL
    else:
        # If no tolerances defined, assume pass
        check.status = QCStatus.PASS
    
    db.commit()
    
    return {
        "message": "Quality test completed",
        "status": check.status.value,
        "actual_value": actual_value,
        "result": "PASS" if check.status == QCStatus.PASS else "FAIL"
    }

@router.post("/checks/{check_id}/approve")
def approve_quality_check(
    check_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_qa)
):
    """Approve a quality check (force pass)"""
    check = db.query(QualityCheck).filter(QualityCheck.id == check_id).first()
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quality check not found"
        )
    
    check.status = QCStatus.PASS
    check.tested_by_id = current_user.id
    check.tested_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Quality check approved"}

@router.post("/checks/{check_id}/reject")
def reject_quality_check(
    check_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_qa)
):
    """Reject a quality check (force fail)"""
    check = db.query(QualityCheck).filter(QualityCheck.id == check_id).first()
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quality check not found"
        )
    
    check.status = QCStatus.FAIL
    check.tested_by_id = current_user.id
    check.tested_at = datetime.utcnow()
    check.notes = f"Rejected: {reason}"
    db.commit()
    
    return {"message": "Quality check rejected"}

@router.get("/checks/batch/{batch_id}", response_model=List[QCSchema])
def get_batch_quality_checks(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get all quality checks for a specific batch"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    checks = db.query(QualityCheck).filter(QualityCheck.batch_id == batch_id).all()
    return checks

@router.get("/checks/batch/{batch_id}/summary")
def get_batch_quality_summary(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get quality summary for a batch"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    checks = db.query(QualityCheck).filter(QualityCheck.batch_id == batch_id).all()
    
    total_checks = len(checks)
    passed_checks = len([c for c in checks if c.status == QCStatus.PASS])
    failed_checks = len([c for c in checks if c.status == QCStatus.FAIL])
    pending_checks = len([c for c in checks if c.status == QCStatus.PENDING])
    
    pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    # Determine overall batch quality status
    if pending_checks > 0:
        overall_status = "PENDING"
    elif failed_checks > 0:
        overall_status = "FAIL"
    else:
        overall_status = "PASS"
    
    return {
        "batch_id": batch_id,
        "batch_number": batch.batch_number,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "pending_checks": pending_checks,
        "pass_rate": round(pass_rate, 2),
        "overall_status": overall_status
    }

@router.get("/dashboard/stats")
def get_quality_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get quality dashboard statistics"""
    total_checks = db.query(QualityCheck).count()
    passed_checks = db.query(QualityCheck).filter(QualityCheck.status == QCStatus.PASS).count()
    failed_checks = db.query(QualityCheck).filter(QualityCheck.status == QCStatus.FAIL).count()
    pending_checks = db.query(QualityCheck).filter(QualityCheck.status == QCStatus.PENDING).count()
    
    # Calculate pass rate
    pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    # Get recent quality trends (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_checks = db.query(QualityCheck).filter(
        QualityCheck.tested_at >= thirty_days_ago
    ).all()
    
    recent_pass_rate = 0
    if recent_checks:
        recent_passed = len([c for c in recent_checks if c.status == QCStatus.PASS])
        recent_pass_rate = (recent_passed / len(recent_checks) * 100)
    
    return {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "pending_checks": pending_checks,
        "pass_rate": round(pass_rate, 2),
        "recent_pass_rate": round(recent_pass_rate, 2)
    }
