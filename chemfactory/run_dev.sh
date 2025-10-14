#!/bin/bash

# ChemFactory MES/ERP Development Runner
echo "🚀 Starting ChemFactory MES/ERP Development Environment..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Initialize database and seed data
echo "🗄️ Setting up database..."
python -c "from app.utils.seed_data import seed_database; seed_database()"

# Start backend in background
echo "🔧 Starting FastAPI backend..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd ../frontend

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Start frontend
echo "🎨 Starting Next.js frontend..."
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
echo "✅ Development environment started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait
