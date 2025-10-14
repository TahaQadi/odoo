from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .security import verify_token
from .settings import settings
from ..db.database import get_db
from ..db.models import User, Role as RoleModel
from ..db.schemas import User as UserSchema
from typing import List

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token)
    username = payload.get("sub")
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    return user


def get_current_user_schema(
    current_user: User = Depends(get_current_user)
) -> UserSchema:
    """Get current user as Pydantic schema."""
    return UserSchema.model_validate(current_user)


def require_roles(required_roles: List[str]):
    """Dependency factory for role-based access control."""
    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Get user roles
        user_roles = db.query(RoleModel).join(User.roles).filter(User.id == current_user.id).all()
        user_role_names = [role.name.value for role in user_roles]
        
        # Check if user has any of the required roles
        if not any(role in user_role_names for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return current_user
    
    return role_checker


# Common role dependencies
require_admin = require_roles(["ADMIN"])
require_production_manager = require_roles(["ADMIN", "PRODUCTION_MANAGER"])
require_operator = require_roles(["ADMIN", "PRODUCTION_MANAGER", "OPERATOR"])
require_warehouse = require_roles(["ADMIN", "WAREHOUSE"])
require_qa = require_roles(["ADMIN", "QA"])
require_finance = require_roles(["ADMIN", "FINANCE"])
require_sales = require_roles(["ADMIN", "SALES"])
require_hr = require_roles(["ADMIN", "HR"])
require_viewer = require_roles(["ADMIN", "PRODUCTION_MANAGER", "OPERATOR", "WAREHOUSE", "QA", "FINANCE", "SALES", "HR", "VIEWER"])
