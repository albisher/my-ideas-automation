#!/bin/bash

# DCS-8000LH Defogger Quick Commands
# Pre-configured with your camera details

# Your Camera Configuration
CAMERA_MAC="B0:C5:54:51:EB:76"
CAMERA_PIN="052446"
WIFI_SSID="SA"
WIFI_PASSWORD="62Dad64Mom"

echo "DCS-8000LH Defogger Quick Commands"
echo "=================================="
echo "Camera MAC: $CAMERA_MAC"
echo "Camera PIN: $CAMERA_PIN"
echo "WiFi SSID: $WIFI_SSID"
echo

# Function to run defogger commands
run_defogger() {
    python3 dcs8000lh-configure.py $CAMERA_MAC $CAMERA_PIN "$@"
}

echo "Available Commands:"
echo "=================="
echo
echo "1. Test Bluetooth Connection:"
echo "   run_defogger --survey"
echo
echo "2. Configure WiFi:"
echo "   run_defogger --essid $WIFI_SSID --wifipw $WIFI_PASSWORD"
echo
echo "3. Check Network Configuration:"
echo "   run_defogger --netconf"
echo
echo "4. Enable HTTP Server:"
echo "   run_defogger --lighttpd"
echo
echo "5. Disable Firmware Signature Verification:"
echo "   run_defogger --unsignedfw"
echo
echo "6. Enable Telnet Access:"
echo "   run_defogger --telnetd"
echo
echo "7. Enable RTSP Streaming:"
echo "   run_defogger --rtsp"
echo
echo "8. Get System Information:"
echo "   run_defogger --sysinfo"
echo
echo "9. Run Custom Command:"
echo "   run_defogger --command 'your_command_here'"
echo

# Interactive menu
while true; do
    echo "Select an option (1-9) or 'q' to quit:"
    read -p "> " choice
    
    case $choice in
        1)
            echo "Testing Bluetooth connection..."
            run_defogger --survey
            ;;
        2)
            echo "Configuring WiFi..."
            run_defogger --essid "$WIFI_SSID" --wifipw "$WIFI_PASSWORD"
            ;;
        3)
            echo "Getting network configuration..."
            run_defogger --netconf
            ;;
        4)
            echo "Enabling HTTP server..."
            run_defogger --lighttpd
            ;;
        5)
            echo "Disabling firmware signature verification..."
            run_defogger --unsignedfw
            ;;
        6)
            echo "Enabling telnet access..."
            run_defogger --telnetd
            ;;
        7)
            echo "Enabling RTSP streaming..."
            run_defogger --rtsp
            ;;
        8)
            echo "Getting system information..."
            run_defogger --sysinfo
            ;;
        9)
            echo "Enter custom command:"
            read -p "Command: " custom_cmd
            run_defogger --command "$custom_cmd"
            ;;
        q)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
    echo
done
