from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import ProductType, HazardClass, StorageFlag, BatchStatus, QCStatus, Role


# Base schemas
class BaseSchema(BaseModel):
    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}


# User schemas
class UserBase(BaseSchema):
    username: str
    email: EmailStr
    full_name: str
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseSchema):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserWithRoles(User):
    roles: List["Role"] = []


# Role schemas
class RoleBase(BaseSchema):
    name: Role
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int
    created_at: datetime


# Authentication schemas
class Token(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseSchema):
    username: Optional[str] = None


class LoginRequest(BaseSchema):
    username: str
    password: str


# Product schemas
class ProductBase(BaseSchema):
    code: str
    name_en: str
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    product_type: ProductType
    unit: str
    density: Optional[float] = None
    cas_number: Optional[str] = None
    hazard_class: HazardClass = HazardClass.NONE
    storage_flag: StorageFlag = StorageFlag.AMBIENT
    shelf_life_days: Optional[int] = None
    msds_url: Optional[str] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseSchema):
    code: Optional[str] = None
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    product_type: Optional[ProductType] = None
    unit: Optional[str] = None
    density: Optional[float] = None
    cas_number: Optional[str] = None
    hazard_class: Optional[HazardClass] = None
    storage_flag: Optional[StorageFlag] = None
    shelf_life_days: Optional[int] = None
    msds_url: Optional[str] = None
    is_active: Optional[bool] = None


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# BOM schemas
class BOMItemBase(BaseSchema):
    product_id: int
    quantity: float
    unit: str
    percentage: Optional[float] = None
    tolerance_min: float = 0.0
    tolerance_max: float = 0.0
    is_optional: bool = False


class BOMItemCreate(BOMItemBase):
    pass


class BOMItem(BOMItemBase):
    id: int
    product: Product
    created_at: datetime


class BOMBase(BaseSchema):
    product_id: int
    version: str
    name_en: str
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    is_released: bool = False


class BOMCreate(BOMBase):
    bom_items: List[BOMItemCreate] = []


class BOMUpdate(BaseSchema):
    version: Optional[str] = None
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    is_released: Optional[bool] = None


class BOM(BOMBase):
    id: int
    product: Product
    created_by: User
    bom_items: List[BOMItem] = []
    created_at: datetime
    updated_at: Optional[datetime] = None


# Manufacturing Order schemas
class ManufacturingOrderBase(BaseSchema):
    mo_number: str
    bom_id: int
    product_id: int
    target_quantity: float
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    priority: int = 1


class ManufacturingOrderCreate(ManufacturingOrderBase):
    pass


class ManufacturingOrderUpdate(BaseSchema):
    mo_number: Optional[str] = None
    bom_id: Optional[int] = None
    product_id: Optional[int] = None
    target_quantity: Optional[float] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    status: Optional[str] = None
    priority: Optional[int] = None


class ManufacturingOrder(ManufacturingOrderBase):
    id: int
    bom: BOM
    product: Product
    created_by: User
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    status: str = "PLANNED"
    created_at: datetime
    updated_at: Optional[datetime] = None


# Batch schemas
class BatchBase(BaseSchema):
    batch_number: str
    product_id: int
    manufacturing_order_id: Optional[int] = None
    target_quantity: float
    actual_quantity: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: BatchStatus = BatchStatus.PLANNED
    operator_id: Optional[int] = None


class BatchCreate(BatchBase):
    pass


class BatchUpdate(BaseSchema):
    batch_number: Optional[str] = None
    product_id: Optional[int] = None
    manufacturing_order_id: Optional[int] = None
    target_quantity: Optional[float] = None
    actual_quantity: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[BatchStatus] = None
    operator_id: Optional[int] = None


class Batch(BatchBase):
    id: int
    product: Product
    manufacturing_order: Optional[ManufacturingOrder] = None
    operator: Optional[User] = None
    created_by: User
    created_at: datetime
    updated_at: Optional[datetime] = None


# Quality Check schemas
class QualityCheckBase(BaseSchema):
    batch_id: int
    test_name_en: str
    test_name_ar: Optional[str] = None
    test_method: Optional[str] = None
    target_value: Optional[float] = None
    tolerance_min: Optional[float] = None
    tolerance_max: Optional[float] = None
    actual_value: Optional[float] = None
    unit: Optional[str] = None
    status: QCStatus = QCStatus.PENDING
    tested_by_id: Optional[int] = None
    tested_at: Optional[datetime] = None
    notes: Optional[str] = None


class QualityCheckCreate(QualityCheckBase):
    pass


class QualityCheckUpdate(BaseSchema):
    test_name_en: Optional[str] = None
    test_name_ar: Optional[str] = None
    test_method: Optional[str] = None
    target_value: Optional[float] = None
    tolerance_min: Optional[float] = None
    tolerance_max: Optional[float] = None
    actual_value: Optional[float] = None
    unit: Optional[str] = None
    status: Optional[QCStatus] = None
    tested_by_id: Optional[int] = None
    tested_at: Optional[datetime] = None
    notes: Optional[str] = None


class QualityCheck(QualityCheckBase):
    id: int
    batch: Batch
    tested_by: Optional[User] = None
    created_at: datetime


# Warehouse schemas
class WarehouseBase(BaseSchema):
    code: str
    name_en: str
    name_ar: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseSchema):
    code: Optional[str] = None
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class Warehouse(WarehouseBase):
    id: int
    created_at: datetime


# Location schemas
class LocationBase(BaseSchema):
    warehouse_id: int
    code: str
    name_en: str
    name_ar: Optional[str] = None
    is_active: bool = True


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseSchema):
    warehouse_id: Optional[int] = None
    code: Optional[str] = None
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    is_active: Optional[bool] = None


class Location(LocationBase):
    id: int
    warehouse: Warehouse
    created_at: datetime


# Inventory schemas
class InventoryItemBase(BaseSchema):
    product_id: int
    batch_id: Optional[int] = None
    location_id: int
    lot_number: Optional[str] = None
    quantity: float
    unit: str
    expiry_date: Optional[datetime] = None
    is_quarantine: bool = False


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseSchema):
    product_id: Optional[int] = None
    batch_id: Optional[int] = None
    location_id: Optional[int] = None
    lot_number: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    expiry_date: Optional[datetime] = None
    is_quarantine: Optional[bool] = None


class InventoryItem(InventoryItemBase):
    id: int
    product: Product
    batch: Optional[Batch] = None
    location: Location
    created_at: datetime
    updated_at: Optional[datetime] = None


# Chart of Accounts schemas
class ChartOfAccountsBase(BaseSchema):
    code: str
    name_en: str
    name_ar: Optional[str] = None
    account_type: str
    parent_id: Optional[int] = None
    is_active: bool = True


class ChartOfAccountsCreate(ChartOfAccountsBase):
    pass


class ChartOfAccountsUpdate(BaseSchema):
    code: Optional[str] = None
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    account_type: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None


class ChartOfAccounts(ChartOfAccountsBase):
    id: int
    parent: Optional["ChartOfAccounts"] = None
    created_at: datetime


# Journal Entry schemas
class JournalLineBase(BaseSchema):
    account_id: int
    description: Optional[str] = None
    debit_amount: float = 0.0
    credit_amount: float = 0.0


class JournalLineCreate(JournalLineBase):
    pass


class JournalLine(JournalLineBase):
    id: int
    account: ChartOfAccounts
    created_at: datetime


class JournalEntryBase(BaseSchema):
    entry_number: str
    description: str
    entry_date: datetime
    journal_lines: List[JournalLineCreate] = []


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryUpdate(BaseSchema):
    entry_number: Optional[str] = None
    description: Optional[str] = None
    entry_date: Optional[datetime] = None
    is_posted: Optional[bool] = None


class JournalEntry(JournalEntryBase):
    id: int
    total_debit: float = 0.0
    total_credit: float = 0.0
    is_posted: bool = False
    created_by: User
    journal_lines: List[JournalLine] = []
    created_at: datetime


# Update forward references
UserWithRoles.model_rebuild()
Role.model_rebuild()
BOMItem.model_rebuild()
BOM.model_rebuild()
ManufacturingOrder.model_rebuild()
Batch.model_rebuild()
QualityCheck.model_rebuild()
Location.model_rebuild()
InventoryItem.model_rebuild()
ChartOfAccounts.model_rebuild()
JournalLine.model_rebuild()
JournalEntry.model_rebuild()
