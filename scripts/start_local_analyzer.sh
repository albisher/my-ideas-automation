#!/bin/bash

# Xiaomi Local Command Analyzer Launcher
# This script starts the local analyzer that runs directly on your macOS machine

echo "🚀 Starting Xiaomi Local Command Analyzer..."
echo "🎯 Target Device: 192.168.68.68"
echo "📊 This will run locally on your machine to learn device commands"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 is available"
echo "🔬 Starting continuous analysis on your local machine..."
echo ""

# Run the analyzer directly on the local machine
python3 scripts/xiaomi_local_analyzer.py
