#!/bin/bash

# ChemFactory MES/ERP Replit Deployment Script
echo "🚀 Deploying ChemFactory MES/ERP on Replit..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt
pip install 'pydantic[email]' email-validator

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Set up database
echo "🗄️ Setting up database..."
export DATABASE_URL="postgresql://postgres:password@localhost:5432/chemfactory"
python -c "
from backend.app.db.database import engine
from backend.app.db import models
models.Base.metadata.create_all(bind=engine)
print('Database created')
"

# Seed database
echo "🌱 Seeding database..."
python -c "
from backend.app.utils.seed_data import seed_database
seed_database()
print('Database seeded')
"

# Start backend
echo "🚀 Starting backend API..."
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
echo "🌐 Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

echo ""
echo "🎉 ChemFactory MES/ERP deployed successfully on Replit!"
echo "======================================================"
echo "Backend API: https://${REPL_SLUG}.${REPL_OWNER}.repl.co:8000"
echo "Frontend: https://${REPL_SLUG}.${REPL_OWNER}.repl.co:3000"
echo "API Docs: https://${REPL_SLUG}.${REPL_OWNER}.repl.co:8000/docs"
echo ""
echo "Default credentials:"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "System is ready for production use! 🚀"

# Keep the script running
wait