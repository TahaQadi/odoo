from sqlalchemy.orm import Session
from ..db.database import SessionLocal
from ..db.models import *
from ..core.security import get_password_hash
from datetime import datetime, timedelta
import random

def seed_database():
    """Seed the database with initial data."""
    db = SessionLocal()
    
    try:
        # Create roles
        roles_data = [
            {"name": Role.ADMIN, "description": "System Administrator"},
            {"name": Role.PRODUCTION_MANAGER, "description": "Production Manager"},
            {"name": Role.OPERATOR, "description": "Production Operator"},
            {"name": Role.WAREHOUSE, "description": "Warehouse Manager"},
            {"name": Role.QA, "description": "Quality Assurance"},
            {"name": Role.FINANCE, "description": "Finance Manager"},
            {"name": Role.SALES, "description": "Sales Manager"},
            {"name": Role.HR, "description": "Human Resources"},
            {"name": Role.VIEWER, "description": "View Only Access"},
        ]
        
        for role_data in roles_data:
            role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not role:
                role = Role(**role_data)
                db.add(role)
        
        db.commit()
        
        # Create admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@chemfactory.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            
            # Assign admin role
            admin_role = db.query(Role).filter(Role.name == Role.ADMIN).first()
            user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
            db.add(user_role)
        
        # Create demo users for each role
        demo_users = [
            {"username": "prod_mgr", "email": "prod@chemfactory.com", "full_name": "Production Manager", "role": Role.PRODUCTION_MANAGER},
            {"username": "operator", "email": "operator@chemfactory.com", "full_name": "Production Operator", "role": Role.OPERATOR},
            {"username": "warehouse", "email": "warehouse@chemfactory.com", "full_name": "Warehouse Manager", "role": Role.WAREHOUSE},
            {"username": "qa", "email": "qa@chemfactory.com", "full_name": "Quality Assurance", "role": Role.QA},
            {"username": "finance", "email": "finance@chemfactory.com", "full_name": "Finance Manager", "role": Role.FINANCE},
            {"username": "sales", "email": "sales@chemfactory.com", "full_name": "Sales Manager", "role": Role.SALES},
        ]
        
        for user_data in demo_users:
            user = db.query(User).filter(User.username == user_data["username"]).first()
            if not user:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=get_password_hash("demo123"),
                    full_name=user_data["full_name"],
                    is_active=True
                )
                db.add(user)
                db.commit()
                
                # Assign role
                role = db.query(Role).filter(Role.name == user_data["role"]).first()
                user_role = UserRole(user_id=user.id, role_id=role.id)
                db.add(user_role)
        
        db.commit()
        
        # Create sample products
        products_data = [
            # Raw Materials
            {
                "code": "RM001", "name_en": "SLES 70%", "name_ar": "سلفات لوريث الصوديوم 70%",
                "product_type": ProductType.RAW_MATERIAL, "unit": "kg", "density": 1.1,
                "hazard_class": HazardClass.NONE, "storage_flag": StorageFlag.AMBIENT,
                "shelf_life_days": 730, "cas_number": "9004-82-4"
            },
            {
                "code": "RM002", "name_en": "CAPB", "name_ar": "كوكاميدو بروبيل بيتين",
                "product_type": ProductType.RAW_MATERIAL, "unit": "kg", "density": 1.0,
                "hazard_class": HazardClass.NONE, "storage_flag": StorageFlag.AMBIENT,
                "shelf_life_days": 730, "cas_number": "61789-40-0"
            },
            {
                "code": "RM003", "name_en": "Fragrance X", "name_ar": "عطر X",
                "product_type": ProductType.RAW_MATERIAL, "unit": "kg", "density": 0.9,
                "hazard_class": HazardClass.NONE, "storage_flag": StorageFlag.AMBIENT,
                "shelf_life_days": 365, "cas_number": "N/A"
            },
            {
                "code": "RM004", "name_en": "Dye Blue 15", "name_ar": "صبغة زرقاء 15",
                "product_type": ProductType.RAW_MATERIAL, "unit": "g", "density": 1.2,
                "hazard_class": HazardClass.NONE, "storage_flag": StorageFlag.AMBIENT,
                "shelf_life_days": 1095, "cas_number": "147-14-8"
            },
            {
                "code": "RM005", "name_en": "Water", "name_ar": "ماء",
                "product_type": ProductType.RAW_MATERIAL, "unit": "L", "density": 1.0,
                "hazard_class": HazardClass.NONE, "storage_flag": StorageFlag.AMBIENT,
                "shelf_life_days": 30, "cas_number": "7732-18-5"
            },
            {
                "code": "RM006", "name_en": "Preservative", "name_ar": "مادة حافظة",
                "product_type": ProductType.RAW_MATERIAL, "unit": "g", "density": 1.0,
                "hazard_class": HazardClass.TOXIC, "storage_flag": StorageFlag.AMBIENT,
                "shelf_life_days": 1095, "cas_number": "N/A"
            },
            # Finished Goods
            {
                "code": "FG001", "name_en": "Dishwash Lemon 1L", "name_ar": "سائل غسيل الأطباق ليمون 1 لتر",
                "product_type": ProductType.FINISHED_GOOD, "unit": "pcs", "density": 1.0,
                "hazard_class": HazardClass.CORROSIVE, "storage_flag": StorageFlag.AMBIENT,
                "shelf_life_days": 1095, "cas_number": "N/A"
            },
            {
                "code": "FG002", "name_en": "Floor Cleaner Pine 4L", "name_ar": "منظف الأرضيات صنوبر 4 لتر",
                "product_type": ProductType.FINISHED_GOOD, "unit": "pcs", "density": 1.0,
                "hazard_class": HazardClass.NONE, "storage_flag": StorageFlag.AMBIENT,
                "shelf_life_days": 1095, "cas_number": "N/A"
            },
        ]
        
        for product_data in products_data:
            product = db.query(Product).filter(Product.code == product_data["code"]).first()
            if not product:
                product = Product(**product_data)
                db.add(product)
        
        db.commit()
        
        # Create warehouse and locations
        warehouse = db.query(Warehouse).filter(Warehouse.code == "WH001").first()
        if not warehouse:
            warehouse = Warehouse(
                code="WH001",
                name_en="Main Warehouse",
                name_ar="المستودع الرئيسي",
                address="Chemical Factory, Industrial Zone",
                is_active=True
            )
            db.add(warehouse)
            db.commit()
        
        # Create locations
        locations_data = [
            {"code": "A01LU", "name_en": "Raw Materials A1", "name_ar": "المواد الخام أ1"},
            {"code": "A02LU", "name_en": "Raw Materials A2", "name_ar": "المواد الخام أ2"},
            {"code": "B01LU", "name_en": "Finished Goods B1", "name_ar": "المنتجات النهائية ب1"},
            {"code": "B02LU", "name_en": "Finished Goods B2", "name_ar": "المنتجات النهائية ب2"},
            {"code": "C01LU", "name_en": "Quarantine", "name_ar": "الحجر الصحي"},
        ]
        
        for loc_data in locations_data:
            location = db.query(Location).filter(Location.code == loc_data["code"]).first()
            if not location:
                location = Location(
                    warehouse_id=warehouse.id,
                    **loc_data,
                    is_active=True
                )
                db.add(location)
        
        db.commit()
        
        # Create BOM for Dishwash Lemon 1L
        dishwash_product = db.query(Product).filter(Product.code == "FG001").first()
        if dishwash_product:
            bom = db.query(BOM).filter(BOM.product_id == dishwash_product.id).first()
            if not bom:
                bom = BOM(
                    product_id=dishwash_product.id,
                    version="1.0",
                    name_en="Dishwash Lemon 1L Formulation",
                    name_ar="تركيبة سائل غسيل الأطباق ليمون 1 لتر",
                    description_en="Standard formulation for dishwashing liquid",
                    description_ar="التركيبة القياسية لسائل غسيل الأطباق",
                    is_released=True,
                    created_by_id=admin_user.id
                )
                db.add(bom)
                db.commit()
                
                # Add BOM items
                bom_items_data = [
                    {"product_code": "RM001", "quantity": 15.0, "unit": "kg", "percentage": 15.0, "tolerance_min": 14.0, "tolerance_max": 16.0},
                    {"product_code": "RM002", "quantity": 5.0, "unit": "kg", "percentage": 5.0, "tolerance_min": 4.5, "tolerance_max": 5.5},
                    {"product_code": "RM003", "quantity": 0.5, "unit": "kg", "percentage": 0.5, "tolerance_min": 0.4, "tolerance_max": 0.6},
                    {"product_code": "RM004", "quantity": 0.1, "unit": "g", "percentage": 0.01, "tolerance_min": 0.005, "tolerance_max": 0.015},
                    {"product_code": "RM005", "quantity": 79.0, "unit": "L", "percentage": 79.0, "tolerance_min": 78.0, "tolerance_max": 80.0},
                    {"product_code": "RM006", "quantity": 0.4, "unit": "g", "percentage": 0.04, "tolerance_min": 0.03, "tolerance_max": 0.05},
                ]
                
                for item_data in bom_items_data:
                    product = db.query(Product).filter(Product.code == item_data["product_code"]).first()
                    if product:
                        bom_item = BOMItem(
                            bom_id=bom.id,
                            product_id=product.id,
                            quantity=item_data["quantity"],
                            unit=item_data["unit"],
                            percentage=item_data["percentage"],
                            tolerance_min=item_data["tolerance_min"],
                            tolerance_max=item_data["tolerance_max"]
                        )
                        db.add(bom_item)
                
                db.commit()
        
        # Create chart of accounts
        coa_data = [
            {"code": "1000", "name_en": "Assets", "name_ar": "الأصول", "account_type": "ASSET"},
            {"code": "1100", "name_en": "Current Assets", "name_ar": "الأصول المتداولة", "account_type": "ASSET", "parent_code": "1000"},
            {"code": "1110", "name_en": "Inventory", "name_ar": "المخزون", "account_type": "ASSET", "parent_code": "1100"},
            {"code": "1120", "name_en": "Raw Materials", "name_ar": "المواد الخام", "account_type": "ASSET", "parent_code": "1110"},
            {"code": "1130", "name_en": "Work in Progress", "name_ar": "الإنتاج تحت التشغيل", "account_type": "ASSET", "parent_code": "1110"},
            {"code": "1140", "name_en": "Finished Goods", "name_ar": "المنتجات النهائية", "account_type": "ASSET", "parent_code": "1110"},
            {"code": "2000", "name_en": "Liabilities", "name_ar": "الخصوم", "account_type": "LIABILITY"},
            {"code": "3000", "name_en": "Equity", "name_ar": "حقوق الملكية", "account_type": "EQUITY"},
            {"code": "4000", "name_en": "Revenue", "name_ar": "الإيرادات", "account_type": "REVENUE"},
            {"code": "5000", "name_en": "Expenses", "name_ar": "المصروفات", "account_type": "EXPENSE"},
            {"code": "5100", "name_en": "Cost of Goods Sold", "name_ar": "تكلفة البضائع المباعة", "account_type": "EXPENSE", "parent_code": "5000"},
        ]
        
        for account_data in coa_data:
            account = db.query(ChartOfAccounts).filter(ChartOfAccounts.code == account_data["code"]).first()
            if not account:
                parent_id = None
                if "parent_code" in account_data:
                    parent = db.query(ChartOfAccounts).filter(ChartOfAccounts.code == account_data["parent_code"]).first()
                    if parent:
                        parent_id = parent.id
                
                account = ChartOfAccounts(
                    code=account_data["code"],
                    name_en=account_data["name_en"],
                    name_ar=account_data["name_ar"],
                    account_type=account_data["account_type"],
                    parent_id=parent_id,
                    is_active=True
                )
                db.add(account)
        
        db.commit()
        
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
