#!/bin/bash

echo "==============================================================================="
echo "🎬 CineAI - Starting Web Application"
echo "==============================================================================="
echo ""
echo "Checking environment..."
echo ""

# Activate virtual environment
source venv/bin/activate

echo "Installing/updating dependencies..."
pip install -q -r requirements.txt

echo ""
echo "==============================================================================="
echo "Starting server..."
echo ""
echo "📱 Open your browser to: http://localhost:8000"
echo "📡 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "==============================================================================="
echo ""

python main.py
