#!/bin/bash

# Xiaomi Local Command Analyzer Launcher
# This script starts the local analyzer that runs continuously on your machine

echo "🚀 Starting Xiaomi Local Command Analyzer..."
echo "🎯 Target Device: 192.168.68.68"
echo "📊 This will run continuously to learn device commands"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Home Assistant container is running
if ! docker ps | grep -q homeassistant; then
    echo "❌ Home Assistant container is not running. Please start it first."
    exit 1
fi

echo "✅ Docker and Home Assistant are running"
echo "🔬 Starting continuous analysis..."
echo ""

# Run the analyzer inside the Home Assistant container
docker exec -it homeassistant python3 /config/scripts/xiaomi_local_analyzer.py
