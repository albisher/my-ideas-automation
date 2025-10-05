#!/bin/bash

# DCS-8000LH RTSP Setup Script
# This script enables RTSP streaming on the DCS-8000LH camera using serial console access

set -e

echo "=== DCS-8000LH RTSP Setup Script ==="
echo "This script will enable RTSP streaming on your DCS-8000LH camera"
echo ""

# Configuration
SERIAL_PORT="/dev/tty.usbserial-31120"
BAUDRATE="115200"
CAMERA_IP=""
ADMIN_PASSWORD=""

# Function to get camera IP
get_camera_ip() {
    echo "Please enter your camera's IP address:"
    read -p "Camera IP: " CAMERA_IP
    
    if [[ -z "$CAMERA_IP" ]]; then
        echo "Error: Camera IP is required"
        exit 1
    fi
    
    echo "Camera IP set to: $CAMERA_IP"
}

# Function to get admin password
get_admin_password() {
    echo "Please enter your camera's admin password (PIN code):"
    read -p "Admin Password: " ADMIN_PASSWORD
    
    if [[ -z "$ADMIN_PASSWORD" ]]; then
        echo "Error: Admin password is required"
        exit 1
    fi
    
    echo "Admin password set"
}

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

# Function to enable web service via serial console
enable_web_service() {
    echo "Enabling web service via serial console..."
    
    # Create a script to send commands via serial
    cat > /tmp/serial_commands.txt << EOF
alpha168
admin
$ADMIN_PASSWORD
grep -Eq ^admin: /etc/passwd || echo admin:x:0:0::/:/bin/sh >>/etc/passwd
grep -Eq ^admin:x: /etc/passwd && echo "admin:$ADMIN_PASSWORD" | chpasswd
tdb set HTTPServer Enable_byte=1
tdb set HTTPAccount AdminPasswd_ss="$ADMIN_PASSWORD"
/etc/rc.d/init.d/extra_lighttpd.sh start
exit
EOF

    echo "Sending commands via serial console..."
    
    # Send commands via serial
    while IFS= read -r line; do
        echo "Sending: $line"
        echo "$line" > "$SERIAL_PORT"
        sleep 1
    done < /tmp/serial_commands.txt
    
    echo "Web service should now be enabled"
}

# Function to test web service
test_web_service() {
    echo "Testing web service..."
    
    # Wait a moment for the service to start
    sleep 5
    
    # Test HTTP access
    if curl -s --connect-timeout 10 "http://$CAMERA_IP" > /dev/null; then
        echo "✅ Web service is accessible at http://$CAMERA_IP"
        return 0
    else
        echo "❌ Web service is not accessible"
        return 1
    fi
}

# Function to download and apply defogger firmware
apply_defogger_firmware() {
    echo "Applying defogger firmware..."
    
    # Check if fw.tar exists
    if [[ ! -f "fw.tar" ]]; then
        echo "Error: fw.tar not found in current directory"
        echo "Please ensure you have the defogger firmware file"
        exit 1
    fi
    
    echo "Uploading firmware to camera..."
    
    # Upload firmware using curl
    if curl --http1.0 -u "admin:$ADMIN_PASSWORD" --form "upload=@fw.tar" "http://$CAMERA_IP/config/firmwareupgrade.cgi"; then
        echo "✅ Firmware uploaded successfully"
        echo "Camera will reboot in about 1 minute..."
    else
        echo "❌ Firmware upload failed"
        exit 1
    fi
}

# Function to test RTSP streaming
test_rtsp_streaming() {
    echo "Testing RTSP streaming..."
    
    # Wait for camera to reboot
    echo "Waiting for camera to reboot (60 seconds)..."
    sleep 60
    
    # Test RTSP stream
    RTSP_URL="rtsp://$CAMERA_IP:554/stream1"
    echo "Testing RTSP stream: $RTSP_URL"
    
    if timeout 10 ffprobe -v quiet -print_format json -show_streams "$RTSP_URL" > /dev/null 2>&1; then
        echo "✅ RTSP streaming is working!"
        echo "RTSP URL: $RTSP_URL"
        return 0
    else
        echo "❌ RTSP streaming test failed"
        echo "You may need to wait longer for the camera to fully boot"
        return 1
    fi
}

# Function to display final information
display_final_info() {
    echo ""
    echo "=== RTSP Setup Complete ==="
    echo ""
    echo "Your DCS-8000LH camera should now support:"
    echo "• RTSP streaming: rtsp://$CAMERA_IP:554/stream1"
    echo "• HTTP streaming: http://$CAMERA_IP/video/mpegts.cgi"
    echo "• Web interface: http://$CAMERA_IP"
    echo ""
    echo "Next steps:"
    echo "1. Test the RTSP stream with VLC or other media player"
    echo "2. Configure Frigate NVR to use this camera"
    echo "3. Set up Home Assistant integration"
    echo "4. Configure Tapo ecosystem integration"
    echo ""
    echo "For troubleshooting, check the camera's web interface at:"
    echo "http://$CAMERA_IP"
}

# Main execution
main() {
    echo "Starting DCS-8000LH RTSP setup..."
    echo ""
    
    # Get configuration
    get_camera_ip
    get_admin_password
    
    # Test serial connection
    test_serial_connection
    
    # Enable web service
    enable_web_service
    
    # Test web service
    if test_web_service; then
        echo "Web service is working, proceeding with firmware update..."
        
        # Apply defogger firmware
        apply_defogger_firmware
        
        # Test RTSP streaming
        test_rtsp_streaming
        
        # Display final information
        display_final_info
    else
        echo "Web service is not accessible. Please check:"
        echo "1. Camera is connected to your network"
        echo "2. Serial console commands were sent successfully"
        echo "3. Camera is powered on and functioning"
        exit 1
    fi
}

# Run main function
main "$@"
