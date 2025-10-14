from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./chemfactory.db"
    
    # JWT
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    refresh_expire_minutes: int = 43200  # 30 days
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # App
    app_name: str = "ChemFactory MES/ERP"
    app_timezone: str = "Asia/Hebron"
    debug: bool = True
    
    # File uploads
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
