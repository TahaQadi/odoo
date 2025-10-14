from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum


class ProductType(str, enum.Enum):
    RAW_MATERIAL = "RAW_MATERIAL"
    INTERMEDIATE = "INTERMEDIATE"
    FINISHED_GOOD = "FINISHED_GOOD"


class HazardClass(str, enum.Enum):
    NONE = "NONE"
    FLAMMABLE = "FLAMMABLE"
    CORROSIVE = "CORROSIVE"
    TOXIC = "TOXIC"
    OXIDIZING = "OXIDIZING"
    ENVIRONMENTAL = "ENVIRONMENTAL"


class StorageFlag(str, enum.Enum):
    AMBIENT = "AMBIENT"
    FRIDGE = "FRIDGE"
    FREEZER = "FREEZER"


class BatchStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ON_HOLD = "ON_HOLD"


class QCStatus(str, enum.Enum):
    PENDING = "PENDING"
    PASS = "PASS"
    FAIL = "FAIL"
    ON_HOLD = "ON_HOLD"


class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    PRODUCTION_MANAGER = "PRODUCTION_MANAGER"
    OPERATOR = "OPERATOR"
    WAREHOUSE = "WAREHOUSE"
    QA = "QA"
    FINANCE = "FINANCE"
    SALES = "SALES"
    HR = "HR"
    VIEWER = "VIEWER"


# User and Authentication Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="user")
    created_batches = relationship("Batch", foreign_keys="Batch.created_by_id", back_populates="created_by")


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(Role), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role")


# Product and Manufacturing Models
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name_en = Column(String(200), nullable=False)
    name_ar = Column(String(200))
    description_en = Column(Text)
    description_ar = Column(Text)
    product_type = Column(Enum(ProductType), nullable=False)
    unit = Column(String(20), nullable=False)  # kg, L, g, ml, pcs
    density = Column(Float)  # kg/L for liquids
    cas_number = Column(String(20))  # Chemical Abstract Service number
    hazard_class = Column(Enum(HazardClass), default=HazardClass.NONE)
    storage_flag = Column(Enum(StorageFlag), default=StorageFlag.AMBIENT)
    shelf_life_days = Column(Integer)
    msds_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bom_items = relationship("BOMItem", back_populates="product")
    batches = relationship("Batch", back_populates="product")
    inventory_items = relationship("InventoryItem", back_populates="product")


class BOM(Base):
    __tablename__ = "boms"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    version = Column(String(20), nullable=False)
    name_en = Column(String(200), nullable=False)
    name_ar = Column(String(200))
    description_en = Column(Text)
    description_ar = Column(Text)
    is_released = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product")
    created_by = relationship("User")
    bom_items = relationship("BOMItem", back_populates="bom")
    manufacturing_orders = relationship("ManufacturingOrder", back_populates="bom")
    
    __table_args__ = (
        Index('idx_bom_product_version', 'product_id', 'version'),
    )


class BOMItem(Base):
    __tablename__ = "bom_items"
    
    id = Column(Integer, primary_key=True, index=True)
    bom_id = Column(Integer, ForeignKey("boms.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    percentage = Column(Float)  # For percentage-based formulations
    tolerance_min = Column(Float, default=0.0)
    tolerance_max = Column(Float, default=0.0)
    is_optional = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    bom = relationship("BOM", back_populates="bom_items")
    product = relationship("Product", back_populates="bom_items")


class ManufacturingOrder(Base):
    __tablename__ = "manufacturing_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    mo_number = Column(String(50), unique=True, index=True, nullable=False)
    bom_id = Column(Integer, ForeignKey("boms.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    target_quantity = Column(Float, nullable=False)
    planned_start_date = Column(DateTime(timezone=True))
    planned_end_date = Column(DateTime(timezone=True))
    actual_start_date = Column(DateTime(timezone=True))
    actual_end_date = Column(DateTime(timezone=True))
    status = Column(String(20), default="PLANNED")
    priority = Column(Integer, default=1)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bom = relationship("BOM", back_populates="manufacturing_orders")
    product = relationship("Product")
    created_by = relationship("User")
    batches = relationship("Batch", back_populates="manufacturing_order")


class Batch(Base):
    __tablename__ = "batches"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String(50), unique=True, index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    manufacturing_order_id = Column(Integer, ForeignKey("manufacturing_orders.id"))
    target_quantity = Column(Float, nullable=False)
    actual_quantity = Column(Float)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    status = Column(Enum(BatchStatus), default=BatchStatus.PLANNED)
    operator_id = Column(Integer, ForeignKey("users.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="batches")
    manufacturing_order = relationship("ManufacturingOrder", back_populates="batches")
    operator = relationship("User", foreign_keys=[operator_id])
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_batches")
    quality_checks = relationship("QualityCheck", back_populates="batch")
    inventory_items = relationship("InventoryItem", back_populates="batch")


# Quality Control Models
class QualityCheck(Base):
    __tablename__ = "quality_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    test_name_en = Column(String(200), nullable=False)
    test_name_ar = Column(String(200))
    test_method = Column(String(100))
    target_value = Column(Float)
    tolerance_min = Column(Float)
    tolerance_max = Column(Float)
    actual_value = Column(Float)
    unit = Column(String(20))
    status = Column(Enum(QCStatus), default=QCStatus.PENDING)
    tested_by_id = Column(Integer, ForeignKey("users.id"))
    tested_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    batch = relationship("Batch", back_populates="quality_checks")
    tested_by = relationship("User")


# Inventory Models
class Warehouse(Base):
    __tablename__ = "warehouses"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name_en = Column(String(100), nullable=False)
    name_ar = Column(String(100))
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    locations = relationship("Location", back_populates="warehouse")


class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    code = Column(String(20), nullable=False)  # e.g., A01LU
    name_en = Column(String(100), nullable=False)
    name_ar = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    warehouse = relationship("Warehouse", back_populates="locations")
    inventory_items = relationship("InventoryItem", back_populates="location")
    
    __table_args__ = (
        Index('idx_location_warehouse_code', 'warehouse_id', 'code'),
    )


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    lot_number = Column(String(50), index=True)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    expiry_date = Column(DateTime(timezone=True))
    is_quarantine = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="inventory_items")
    batch = relationship("Batch", back_populates="inventory_items")
    location = relationship("Location", back_populates="inventory_items")
    
    __table_args__ = (
        Index('idx_inventory_product_location', 'product_id', 'location_id'),
        Index('idx_inventory_lot', 'lot_number'),
    )


# Accounting Models
class ChartOfAccounts(Base):
    __tablename__ = "chart_of_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name_en = Column(String(200), nullable=False)
    name_ar = Column(String(200))
    account_type = Column(String(50), nullable=False)  # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    parent_id = Column(Integer, ForeignKey("chart_of_accounts.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    parent = relationship("ChartOfAccounts", remote_side=[id])


class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    entry_number = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    entry_date = Column(DateTime(timezone=True), nullable=False)
    total_debit = Column(Float, default=0.0)
    total_credit = Column(Float, default=0.0)
    is_posted = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    created_by = relationship("User")
    journal_lines = relationship("JournalLine", back_populates="journal_entry")


class JournalLine(Base):
    __tablename__ = "journal_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False)
    description = Column(Text)
    debit_amount = Column(Float, default=0.0)
    credit_amount = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="journal_lines")
    account = relationship("ChartOfAccounts")
