#!/bin/bash
echo "🚀 Starting ChemFactory MES/ERP Production Environment"
echo "====================================================="

# Start backend
echo "Starting backend API..."
cd production/backend
export DATABASE_URL="sqlite:///./production.db"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

echo ""
echo "🎉 ChemFactory MES/ERP Production Environment Started!"
echo "====================================================="
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Default credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait
