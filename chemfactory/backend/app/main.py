from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.settings import settings
from .api import auth, products, manufacturing, batches, quality, monitoring, reports
from .db.database import engine
from .db import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Chemical Factory MES/ERP System with AI and Real-time Monitoring",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(manufacturing.router, prefix="/api/v1")
app.include_router(batches.router, prefix="/api/v1")
app.include_router(quality.router, prefix="/api/v1")
app.include_router(monitoring.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to ChemFactory MES/ERP v2.0",
        "version": "2.0.0",
        "docs": "/docs",
        "features": [
            "Product Management",
            "Manufacturing Orders",
            "Batch Tracking",
            "Quality Control",
            "Real-time Monitoring",
            "AI Integration",
            "Workflow Engine",
            "Mobile App",
            "Advanced Reporting"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/dashboard/stats")
def get_dashboard_stats():
    """Get overall dashboard statistics"""
    return {
        "system_status": "operational",
        "features_available": [
            "products",
            "manufacturing",
            "batches", 
            "quality",
            "monitoring",
            "reports",
            "ai_analytics",
            "workflows",
            "mobile_app"
        ],
        "api_version": "2.0.0"
    }
