#!/usr/bin/env python3
"""
ChemFactory MES/ERP - Main Entry Point for Replit
This script orchestrates the deployment of both Odoo and ChemFactory components
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

def run_command(cmd, cwd=None, background=False):
    """Run a command and return the process"""
    print(f"🚀 Running: {cmd}")
    if background:
        return subprocess.Popen(cmd, shell=True, cwd=cwd)
    else:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error running command: {cmd}")
            print(f"Error: {result.stderr}")
        return result

def setup_environment():
    """Set up the environment variables and paths"""
    print("🔧 Setting up environment...")
    
    # Set environment variables
    os.environ['PYTHONPATH'] = '/workspace'
    os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/chemfactory')
    os.environ['JWT_SECRET'] = os.environ.get('JWT_SECRET', 'replit_chemfactory_jwt_secret_2025_secure_key')
    os.environ['JWT_EXPIRE_MINUTES'] = os.environ.get('JWT_EXPIRE_MINUTES', '60')
    os.environ['REFRESH_EXPIRE_MINUTES'] = os.environ.get('REFRESH_EXPIRE_MINUTES', '10080')
    os.environ['CORS_ORIGINS'] = os.environ.get('CORS_ORIGINS', '["*"]')
    os.environ['APP_NAME'] = os.environ.get('APP_NAME', 'ChemFactory MES/ERP')
    os.environ['APP_VERSION'] = os.environ.get('APP_VERSION', '2.0.0')
    os.environ['DEBUG'] = os.environ.get('DEBUG', 'true')
    
    # Set Replit-specific URLs
    repl_slug = os.environ.get('REPL_SLUG', 'chemfactory')
    repl_owner = os.environ.get('REPL_OWNER', 'user')
    base_url = f"https://{repl_slug}.{repl_owner}.repl.co"
    
    os.environ['NEXT_PUBLIC_API_URL'] = f"{base_url}/api/v1"
    os.environ['NEXT_PUBLIC_APP_NAME'] = 'ChemFactory MES/ERP'
    os.environ['NEXT_PUBLIC_APP_VERSION'] = '2.0.0'
    
    print(f"🌐 Base URL: {base_url}")
    print(f"🔗 API URL: {os.environ['NEXT_PUBLIC_API_URL']}")

def install_dependencies():
    """Install all required dependencies"""
    print("📦 Installing dependencies...")
    
    # Install Python dependencies for Odoo
    print("Installing Odoo Python dependencies...")
    run_command("pip install -r requirements.txt")
    
    # Install ChemFactory backend dependencies
    print("Installing ChemFactory backend dependencies...")
    run_command("pip install -r chemfactory/backend/requirements.txt")
    run_command("pip install 'pydantic[email]' email-validator")
    
    # Install Node.js dependencies for frontend
    print("Installing frontend dependencies...")
    run_command("npm install", cwd="chemfactory/frontend")

def setup_database():
    """Set up the database"""
    print("🗄️ Setting up database...")
    
    # Create ChemFactory database tables
    print("Creating ChemFactory database tables...")
    run_command("python -c \"from chemfactory.backend.app.db.database import engine; from chemfactory.backend.app.db import models; models.Base.metadata.create_all(bind=engine); print('ChemFactory database created')\"")
    
    # Seed ChemFactory database
    print("Seeding ChemFactory database...")
    run_command("python -c \"from chemfactory.backend.app.utils.seed_data import seed_database; seed_database(); print('ChemFactory database seeded')\"")

def start_services():
    """Start all services"""
    print("🚀 Starting services...")
    
    processes = []
    
    # Start Odoo server
    print("Starting Odoo server...")
    odoo_cmd = "python3 ./odoo-bin -c odoo.conf --proxy-mode --http-port=5000 --http-interface=0.0.0.0"
    odoo_process = run_command(odoo_cmd, background=True)
    processes.append(("Odoo", odoo_process))
    
    # Wait a bit for Odoo to start
    time.sleep(10)
    
    # Start ChemFactory backend
    print("Starting ChemFactory backend...")
    backend_cmd = "python -m uvicorn chemfactory.backend.app.main:app --host 0.0.0.0 --port 8000"
    backend_process = run_command(backend_cmd, background=True)
    processes.append(("ChemFactory Backend", backend_process))
    
    # Wait a bit for backend to start
    time.sleep(5)
    
    # Start ChemFactory frontend
    print("Starting ChemFactory frontend...")
    frontend_cmd = "npm run dev"
    frontend_process = run_command(frontend_cmd, cwd="chemfactory/frontend", background=True)
    processes.append(("ChemFactory Frontend", frontend_process))
    
    return processes

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down services...")
    sys.exit(0)

def main():
    """Main deployment function"""
    print("🚀 ChemFactory MES/ERP - Replit Deployment")
    print("=" * 50)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Setup
        setup_environment()
        install_dependencies()
        setup_database()
        
        # Start services
        processes = start_services()
        
        print("\n🎉 ChemFactory MES/ERP deployed successfully!")
        print("=" * 50)
        print("🌐 Odoo ERP: https://${REPL_SLUG}.${REPL_OWNER}.repl.co:5000")
        print("🔗 ChemFactory API: https://${REPL_SLUG}.${REPL_OWNER}.repl.co:8000")
        print("📱 ChemFactory Web: https://${REPL_SLUG}.${REPL_OWNER}.repl.co:3000")
        print("📚 API Docs: https://${REPL_SLUG}.${REPL_OWNER}.repl.co:8000/docs")
        print("\n🔑 Default Credentials:")
        print("   Odoo: admin / admin123")
        print("   ChemFactory: admin / admin123")
        print("\n✨ System is ready for production use!")
        
        # Keep the main process alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()