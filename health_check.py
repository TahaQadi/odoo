#!/usr/bin/env python3
"""
Health Check Script for ChemFactory MES/ERP
Checks the status of all services and components
"""

import requests
import sys
import time
import subprocess
import os
from urllib.parse import urljoin

def check_service(url, name, timeout=5):
    """Check if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name}: OK ({response.status_code})")
            return True
        else:
            print(f"❌ {name}: Error ({response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: Connection failed - {e}")
        return False

def check_process(process_name):
    """Check if a process is running"""
    try:
        result = subprocess.run(['pgrep', '-f', process_name], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {process_name}: Running (PID: {result.stdout.strip()})")
            return True
        else:
            print(f"❌ {process_name}: Not running")
            return False
    except Exception as e:
        print(f"❌ {process_name}: Check failed - {e}")
        return False

def main():
    """Main health check function"""
    print("🏥 ChemFactory MES/ERP Health Check")
    print("=" * 40)
    
    # Get Replit environment variables
    repl_slug = os.environ.get('REPL_SLUG', 'chemfactory')
    repl_owner = os.environ.get('REPL_OWNER', 'user')
    base_url = f"https://{repl_slug}.{repl_owner}.repl.co"
    
    print(f"🌐 Base URL: {base_url}")
    print()
    
    # Check processes
    print("🔍 Checking Processes:")
    processes = [
        'odoo-bin',
        'uvicorn',
        'npm'
    ]
    
    process_status = {}
    for process in processes:
        process_status[process] = check_process(process)
    
    print()
    
    # Check services
    print("🌐 Checking Services:")
    services = [
        (f"{base_url}:5000", "Odoo ERP"),
        (f"{base_url}:8000/health", "ChemFactory API"),
        (f"{base_url}:8000/docs", "API Documentation"),
        (f"{base_url}:3000", "ChemFactory Frontend")
    ]
    
    service_status = {}
    for url, name in services:
        service_status[name] = check_service(url, name)
    
    print()
    
    # Summary
    print("📊 Health Check Summary:")
    print("-" * 30)
    
    total_processes = len(processes)
    running_processes = sum(1 for status in process_status.values() if status)
    
    total_services = len(services)
    healthy_services = sum(1 for status in service_status.values() if status)
    
    print(f"Processes: {running_processes}/{total_processes} running")
    print(f"Services: {healthy_services}/{total_services} healthy")
    
    if running_processes == total_processes and healthy_services == total_services:
        print("🎉 All systems operational!")
        return 0
    else:
        print("⚠️  Some issues detected. Check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())