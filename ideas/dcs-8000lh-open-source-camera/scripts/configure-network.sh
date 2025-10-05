#!/bin/bash

# DCS-8000LH Network Configuration Script
# This script configures the camera to connect to your specific network

set -e

echo "=== DCS-8000LH Network Configuration ==="
echo "Configuring camera to connect to network: SA"
echo ""

# Network configuration
NETWORK_SSID="SA"
NETWORK_PASSWORD="62Dad64Mom"
SERIAL_PORT="/dev/tty.usbserial-31120"
BAUDRATE="115200"

# Function to test serial connection
test_serial_connection() {
    echo "Testing serial connection..."
    
    if [[ ! -e "$SERIAL_PORT" ]]; then
        echo "Error: Serial port $SERIAL_PORT not found"
        echo "Please check your USB-to-TTL adapter connection"
        exit 1
    fi
    
    echo "Serial port found: $SERIAL_PORT"
}

# Function to configure network via serial console
configure_network() {
    echo "Configuring network via serial console..."
    
    # Create a script to send network configuration commands
    cat > /tmp/network_commands.txt << EOF
alpha168
admin
admin
wifi_scan
wifi_connect "$NETWORK_SSID" "$NETWORK_PASSWORD"
ifconfig
exit
EOF

    echo "Sending network configuration commands..."
    
    # Send commands via serial
    while IFS= read -r line; do
        echo "Sending: $line"
        echo "$line" > "$SERIAL_PORT"
        sleep 2
    done < /tmp/network_commands.txt
    
    echo "Network configuration sent"
}

# Function to get camera IP
get_camera_ip() {
    echo "Getting camera IP address..."
    
    # Try to get IP from serial console
    cat > /tmp/get_ip_commands.txt << EOF
alpha168
admin
admin
ifconfig
exit
EOF

    echo "Getting network information..."
    
    # Send commands and capture response
    while IFS= read -r line; do
        echo "$line" > "$SERIAL_PORT"
        sleep 1
    done < /tmp/get_ip_commands.txt
    
    echo "Network configuration completed"
}

# Function to test network connectivity
test_network_connectivity() {
    echo "Testing network connectivity..."
    
    # Wait for camera to connect to network
    echo "Waiting for camera to connect to network (30 seconds)..."
    sleep 30
    
    # Try to find camera IP
    echo "Scanning for camera on network..."
    
    # Check common IP ranges
    for ip in 192.168.68.{1..254}; do
        if ping -c 1 -W 1000 "$ip" > /dev/null 2>&1; then
            echo "Found active IP: $ip"
            # Try to check if it's the camera
            if curl -s --connect-timeout 5 "http://$ip" > /dev/null 2>&1; then
                echo "✅ Camera found at: $ip"
                echo "$ip" > camera_ip.txt
                return 0
            fi
        fi
    done
    
    echo "❌ Camera not found on network"
    return 1
}

# Function to display final information
display_final_info() {
    if [[ -f "camera_ip.txt" ]]; then
        CAMERA_IP=$(cat camera_ip.txt)
        echo ""
        echo "=== Network Configuration Complete ==="
        echo ""
        echo "✅ Camera is connected to network: $NETWORK_SSID"
        echo "✅ Camera IP address: $CAMERA_IP"
        echo ""
        echo "🌐 Camera Access:"
        echo "• Web Interface: http://$CAMERA_IP"
        echo "• RTSP Stream: rtsp://admin:admin@$CAMERA_IP:554/stream1"
        echo "• HTTP Stream: http://$CAMERA_IP/video/mpegts.cgi"
        echo ""
        echo "📱 Next Steps:"
        echo "1. Test camera access: http://$CAMERA_IP"
        echo "2. Run the complete system setup"
        echo "3. Configure Frigate NVR"
        echo "4. Set up Home Assistant"
        echo ""
        echo "🔧 Management:"
        echo "• Camera IP saved to: camera_ip.txt"
        echo "• Network: $NETWORK_SSID"
        echo "• Password: $NETWORK_PASSWORD"
    else
        echo ""
        echo "❌ Network configuration failed"
        echo "Please check:"
        echo "1. Camera is powered on"
        echo "2. Serial connection is working"
        echo "3. Network credentials are correct"
        echo "4. Camera is within range of network"
    fi
}

# Main execution
main() {
    echo "Starting network configuration..."
    echo ""
    
    # Test serial connection
    test_serial_connection
    
    # Configure network
    configure_network
    
    # Get camera IP
    get_camera_ip
    
    # Test network connectivity
    if test_network_connectivity; then
        display_final_info
    else
        echo "Network configuration completed, but camera IP not found"
        echo "Please check the camera's web interface manually"
    fi
}

# Run main function
main "$@"
