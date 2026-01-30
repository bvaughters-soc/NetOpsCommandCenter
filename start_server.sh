#!/bin/bash
# Quick Start Script for NetOps Command Center

echo "=========================================="
echo "NetOps Command Center - Quick Start"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✓ Python 3 found"

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

echo "✓ pip found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create static directory if it doesn't exist
mkdir -p static

echo ""
echo "🚀 Starting NetOps Command Center..."
echo ""
echo "=========================================="
echo "Server will start on http://localhost:5000"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 api_server.py
