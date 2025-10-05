#!/bin/bash
# Xiaomi Command Capture Script
# This script will capture traffic between your phone and Xiaomi device

echo "🎯 Xiaomi Command Capture Script"
echo "================================"
echo ""
echo "📱 Your phone: 192.168.68.65"
echo "🎯 Xiaomi device: 192.168.68.62"
echo "🔍 MAC: d4:35:38:a:bc:57"
echo ""
echo "🚀 Starting tcpdump capture..."
echo "📱 Send commands from your phone now!"
echo "🛑 Press Ctrl+C to stop when done"
echo ""
echo "📊 Capture will be saved to: xiaomi_commands_$(date +%Y%m%d_%H%M%S).pcap"
echo ""

# Create timestamped filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="xiaomi_commands_${TIMESTAMP}.pcap"

# Start tcpdump capture
sudo tcpdump -i en1 -n -l -A -s 0 "host 192.168.68.65 and host 192.168.68.62" -w "$OUTPUT_FILE"

echo ""
echo "✅ Capture completed!"
echo "📁 File saved: $OUTPUT_FILE"
echo "📊 File size: $(ls -lh "$OUTPUT_FILE" | awk '{print $5}')"
echo ""
echo "🔍 To analyze the capture:"
echo "   tcpdump -r $OUTPUT_FILE"
echo "   tcpdump -r $OUTPUT_FILE -A"
echo ""
