#!/bin/bash
echo ""
echo "=========================================="
echo "  BusinessPulse Analytics Platform v1.0"
echo "=========================================="
echo ""

# Install dependencies
echo "Installing dependencies..."
pip3 install flask flask-sqlalchemy -q 2>/dev/null || pip install flask flask-sqlalchemy -q

echo ""
echo "Starting server at http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

# Open browser after 2 seconds
(sleep 2 && open "http://localhost:5000" 2>/dev/null || xdg-open "http://localhost:5000" 2>/dev/null) &

python3 app.py 2>/dev/null || python app.py
