from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db.database import get_db
from ..db.models import Product, ProductType, HazardClass, StorageFlag
from ..db.schemas import Product as ProductSchema, ProductCreate, ProductUpdate
from ..core.dependencies import require_viewer, require_admin

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[ProductSchema])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    product_type: Optional[ProductType] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get all products with filtering and pagination"""
    query = db.query(Product)
    
    if product_type:
        query = query.filter(Product.product_type == product_type)
    
    if search:
        query = query.filter(
            (Product.name_en.ilike(f"%{search}%")) |
            (Product.name_ar.ilike(f"%{search}%")) |
            (Product.code.ilike(f"%{search}%"))
        )
    
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductSchema)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get a specific product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.post("/", response_model=ProductSchema)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Create a new product"""
    # Check if product code already exists
    existing_product = db.query(Product).filter(Product.code == product.code).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product code already exists"
        )
    
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=ProductSchema)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Update an existing product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if new code conflicts with existing products
    if product_update.code and product_update.code != db_product.code:
        existing_product = db.query(Product).filter(
            Product.code == product_update.code,
            Product.id != product_id
        ).first()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product code already exists"
            )
    
    # Update fields
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Delete a product (soft delete by setting is_active=False)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db_product.is_active = False
    db.commit()
    return {"message": "Product deactivated successfully"}

@router.get("/search/{query}", response_model=List[ProductSchema])
def search_products(
    query: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Search products by name or code"""
    products = db.query(Product).filter(
        (Product.name_en.ilike(f"%{query}%")) |
        (Product.name_ar.ilike(f"%{query}%")) |
        (Product.code.ilike(f"%{query}%"))
    ).limit(limit).all()
    
    return products

@router.get("/by-type/{product_type}", response_model=List[ProductSchema])
def get_products_by_type(
    product_type: ProductType,
    db: Session = Depends(get_db),
    current_user = Depends(require_viewer)
):
    """Get products by type"""
    products = db.query(Product).filter(
        Product.product_type == product_type,
        Product.is_active == True
    ).all()
    
    return products
