#!/bin/bash

# Google Home Integration Setup Script for Home Assistant
# This script helps set up Google Home devices with Home Assistant

echo "🏠 Google Home Integration Setup for Home Assistant"
echo "=================================================="

# Check if Home Assistant is running
echo "📡 Checking Home Assistant status..."
if ! docker ps | grep -q homeassistant; then
    echo "❌ Home Assistant container is not running. Starting it now..."
    cd /Users/amac/myIdeas
    docker-compose up -d homeassistant
    echo "⏳ Waiting for Home Assistant to start..."
    sleep 30
else
    echo "✅ Home Assistant is running"
fi

# Check network connectivity
echo "🌐 Checking network connectivity..."
if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    echo "✅ Internet connection is working"
else
    echo "❌ No internet connection. Please check your network."
    exit 1
fi

# Display configuration instructions
echo ""
echo "📋 Configuration Steps:"
echo "======================"
echo ""
echo "1. 📱 Open Home Assistant in your browser:"
echo "   http://localhost:8123"
echo ""
echo "2. 🔧 Go to Settings > Devices & Services"
echo ""
echo "3. ➕ Click 'Add Integration' and search for:"
echo "   - 'Google Cast' (for Google Home devices)"
echo "   - 'Google Assistant' (for voice control)"
echo ""
echo "4. 🔍 The system will automatically discover your Google Home devices"
echo ""
echo "5. 🎯 Follow the on-screen setup instructions"
echo ""

# Check if devices are discoverable
echo "🔍 Checking for Google Home devices on network..."
echo "This may take a moment..."

# Use nmap to scan for Google Cast devices (port 8008)
if command -v nmap > /dev/null 2>&1; then
    echo "Scanning for Google Cast devices..."
    nmap -p 8008 --open 192.168.1.0/24 2>/dev/null | grep -E "(Nmap scan report|8008/tcp.*open)" || echo "No Google Cast devices found on port 8008"
else
    echo "⚠️  nmap not found. Install with: brew install nmap"
    echo "   Or manually check your router's device list for Google Home devices"
fi

echo ""
echo "📚 Documentation:"
echo "================="
echo "📖 Integration guide: homeassistant/docs/voice-assistants/google-home-integration.md"
echo "🌐 Home Assistant docs: https://www.home-assistant.io/integrations/google_cast/"
echo ""

echo "✅ Setup script completed!"
echo ""
echo "Next steps:"
echo "1. Access Home Assistant at http://localhost:8123"
echo "2. Add Google Cast and Google Assistant integrations"
echo "3. Follow the setup wizard"
echo "4. Test your Google Home devices"
echo ""
echo "🎉 Happy automating!"
