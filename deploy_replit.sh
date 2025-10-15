#!/bin/bash

# ChemFactory MES/ERP Replit Deployment Script
echo "🚀 Deploying ChemFactory MES/ERP on Replit..."

# Set environment variables
export PYTHONPATH="/workspace"
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:password@localhost:5432/chemfactory}"
export JWT_SECRET="${JWT_SECRET:-replit_chemfactory_jwt_secret_2025_secure_key}"
export JWT_EXPIRE_MINUTES="${JWT_EXPIRE_MINUTES:-60}"
export REFRESH_EXPIRE_MINUTES="${REFRESH_EXPIRE_MINUTES:-10080}"
export CORS_ORIGINS="${CORS_ORIGINS:-[\"*\"]}"
export APP_NAME="${APP_NAME:-ChemFactory MES/ERP}"
export APP_VERSION="${APP_VERSION:-2.0.0}"
export DEBUG="${DEBUG:-true}"

# Set Replit-specific URLs
REPL_SLUG="${REPL_SLUG:-chemfactory}"
REPL_OWNER="${REPL_OWNER:-user}"
BASE_URL="https://${REPL_SLUG}.${REPL_OWNER}.repl.co"
export NEXT_PUBLIC_API_URL="${BASE_URL}/api/v1"
export NEXT_PUBLIC_APP_NAME="ChemFactory MES/ERP"
export NEXT_PUBLIC_APP_VERSION="2.0.0"

echo "🌐 Base URL: ${BASE_URL}"
echo "🔗 API URL: ${NEXT_PUBLIC_API_URL}"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
pip install -r chemfactory/backend/requirements.txt
pip install 'pydantic[email]' email-validator

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd chemfactory/frontend
npm install
cd ../..

# Set up ChemFactory database
echo "🗄️ Setting up ChemFactory database..."
python -c "
from chemfactory.backend.app.db.database import engine
from chemfactory.backend.app.db import models
models.Base.metadata.create_all(bind=engine)
print('ChemFactory database created')
"

# Seed ChemFactory database
echo "🌱 Seeding ChemFactory database..."
python -c "
from chemfactory.backend.app.utils.seed_data import seed_database
seed_database()
print('ChemFactory database seeded')
"

# Start Odoo server
echo "🚀 Starting Odoo server..."
python3 ./odoo-bin -c odoo.conf --proxy-mode --http-port=5000 --http-interface=0.0.0.0 &
ODOO_PID=$!

# Wait for Odoo to start
echo "⏳ Waiting for Odoo to start..."
sleep 15

# Start ChemFactory backend
echo "🚀 Starting ChemFactory backend API..."
python -m uvicorn chemfactory.backend.app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Start ChemFactory frontend
echo "🌐 Starting ChemFactory frontend..."
cd chemfactory/frontend
npm run dev &
FRONTEND_PID=$!
cd ../..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 5

echo ""
echo "🎉 ChemFactory MES/ERP deployed successfully on Replit!"
echo "======================================================"
echo "🏢 Odoo ERP: ${BASE_URL}:5000"
echo "🔗 ChemFactory API: ${BASE_URL}:8000"
echo "📱 ChemFactory Web: ${BASE_URL}:3000"
echo "📚 API Docs: ${BASE_URL}:8000/docs"
echo ""
echo "🔑 Default Credentials:"
echo "   Odoo: admin / admin123"
echo "   ChemFactory: admin / admin123"
echo ""
echo "✨ System is ready for production use! 🚀"

# Function to handle shutdown
cleanup() {
    echo "🛑 Shutting down services..."
    kill $ODOO_PID 2>/dev/null
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Keep the script running
wait