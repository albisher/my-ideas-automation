#!/bin/bash

# DCS-8000LH Defogger Setup Script
# Complete automated setup for defogger method

set -e

# Configuration
CAMERA_MAC="B0:C5:54:51:EB:76"   # Your camera MAC
CAMERA_PIN="052446"              # Your camera PIN
WIFI_SSID="SA"                   # Your WiFi name
WIFI_PASSWORD="62Dad64Mom"       # Your WiFi password
CAMERA_IP=""                     # Will be detected automatically

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root"
    fi
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
    fi
    
    # Check bluepy
    if ! python3 -c "import bluepy" &> /dev/null; then
        error "bluepy library is required. Install with: pip3 install bluepy"
    fi
    
    # Check Bluetooth
    if ! hciconfig &> /dev/null; then
        error "Bluetooth is required but not available"
    fi
    
    # Check if camera script exists
    if [[ ! -f "dcs8000lh-configure.py" ]]; then
        error "dcs8000lh-configure.py not found in current directory"
    fi
    
    success "Prerequisites check passed"
}

# Test Bluetooth connection
test_bluetooth() {
    log "Testing Bluetooth connection to camera..."
    
    if python3 dcs8000lh-configure.py $CAMERA_MAC $CAMERA_PIN --survey > /dev/null 2>&1; then
        success "Bluetooth connection successful"
    else
        error "Failed to connect to camera via Bluetooth. Check MAC address and PIN code."
    fi
}

# Configure WiFi
configure_wifi() {
    log "Configuring camera WiFi connection..."
    
    if python3 dcs8000lh-configure.py $CAMERA_MAC $CAMERA_PIN --essid "$WIFI_SSID" --wifipw "$WIFI_PASSWORD"; then
        success "WiFi configuration successful"
    else
        error "Failed to configure WiFi"
    fi
}

# Get camera IP
get_camera_ip() {
    log "Getting camera IP address..."
    
    # Wait for camera to connect
    sleep 10
    
    # Get network configuration
    NETWORK_CONFIG=$(python3 dcs8000lh-configure.py $CAMERA_MAC $CAMERA_PIN --netconf 2>/dev/null)
    
    if [[ $? -eq 0 ]]; then
        CAMERA_IP=$(echo "$NETWORK_CONFIG" | grep -oP 'ip config:.*?I=\K[0-9.]+' | head -1)
        if [[ -n "$CAMERA_IP" ]]; then
            success "Camera IP detected: $CAMERA_IP"
        else
            error "Failed to detect camera IP address"
        fi
    else
        error "Failed to get network configuration"
    fi
}

# Enable HTTP server
enable_http_server() {
    log "Enabling HTTP server on camera..."
    
    if python3 dcs8000lh-configure.py $CAMERA_MAC $CAMERA_PIN --lighttpd; then
        success "HTTP server enabled"
    else
        error "Failed to enable HTTP server"
    fi
}

# Disable firmware signature verification
disable_signature_verification() {
    log "Disabling firmware signature verification..."
    
    if python3 dcs8000lh-configure.py $CAMERA_MAC $CAMERA_PIN --unsignedfw; then
        success "Firmware signature verification disabled"
    else
        error "Failed to disable firmware signature verification"
    fi
}

# Enable telnet
enable_telnet() {
    log "Enabling telnet access..."
    
    if python3 dcs8000lh-configure.py $CAMERA_MAC $CAMERA_PIN --telnetd; then
        success "Telnet access enabled"
    else
        error "Failed to enable telnet access"
    fi
}

# Enable RTSP
enable_rtsp() {
    log "Enabling RTSP streaming..."
    
    if python3 dcs8000lh-configure.py $CAMERA_MAC $CAMERA_PIN --rtsp; then
        success "RTSP streaming enabled"
    else
        error "Failed to enable RTSP streaming"
    fi
}

# Build custom firmware
build_firmware() {
    log "Building custom firmware..."
    
    if [[ -f "Makefile" ]]; then
        if make; then
            success "Custom firmware built successfully"
        else
            error "Failed to build custom firmware"
        fi
    else
        warning "Makefile not found, skipping firmware build"
    fi
}

# Flash custom firmware
flash_firmware() {
    log "Flashing custom firmware..."
    
    if [[ -f "fw.tar" ]]; then
        if curl --http1.0 -u admin:$CAMERA_PIN --form upload=@fw.tar http://$CAMERA_IP/config/firmwareupgrade.cgi; then
            success "Custom firmware flashed successfully"
            log "Camera will reboot automatically..."
            sleep 30
        else
            error "Failed to flash custom firmware"
        fi
    else
        warning "fw.tar not found, skipping firmware flash"
    fi
}

# Test streaming
test_streaming() {
    log "Testing streaming endpoints..."
    
    # Test HTTP streaming
    if curl -s -u admin:$CAMERA_PIN http://$CAMERA_IP/video/mpegts.cgi > /dev/null; then
        success "HTTP MPEG-TS streaming working"
    else
        warning "HTTP MPEG-TS streaming not working"
    fi
    
    # Test RTSP streaming
    if curl -s -u admin:$CAMERA_PIN http://$CAMERA_IP/config/rtspurl.cgi?profileid=1 > /dev/null; then
        success "RTSP streaming working"
    else
        warning "RTSP streaming not working"
    fi
    
    # Test NIPCA API
    if curl -s -u admin:$CAMERA_PIN http://$CAMERA_IP/common/info.cgi > /dev/null; then
        success "NIPCA API working"
    else
        warning "NIPCA API not working"
    fi
}

# Display results
display_results() {
    log "Defogger setup complete!"
    echo
    echo "Camera Information:"
    echo "  IP Address: $CAMERA_IP"
    echo "  Admin User: admin"
    echo "  Password: $CAMERA_PIN"
    echo
    echo "Streaming Endpoints:"
    echo "  HTTP MPEG-TS: http://$CAMERA_IP/video/mpegts.cgi"
    echo "  HTTP FLV: http://$CAMERA_IP/video/flv.cgi"
    echo "  RTSP: rtsp://$CAMERA_IP/live/profile.0"
    echo
    echo "API Endpoints:"
    echo "  Camera Info: http://$CAMERA_IP/common/info.cgi"
    echo "  LED Control: http://$CAMERA_IP/config/led.cgi?led=off"
    echo "  Date/Time: http://$CAMERA_IP/config/datetime.cgi"
    echo
    echo "Telnet Access:"
    echo "  telnet $CAMERA_IP"
    echo "  Username: admin"
    echo "  Password: $CAMERA_PIN"
    echo
    echo "Next Steps:"
    echo "  1. Test streaming with VLC or similar player"
    echo "  2. Configure Home Assistant integration"
    echo "  3. Set up Frigate NVR if desired"
    echo
    success "Setup complete! Your camera is now defogged and ready for local streaming."
}

# Main execution
main() {
    echo "DCS-8000LH Defogger Setup Script"
    echo "================================="
    echo
    
    # Configuration is already set with your camera details
    log "Using camera MAC: $CAMERA_MAC"
    log "Using camera PIN: $CAMERA_PIN"
    log "Using WiFi SSID: $WIFI_SSID"
    
    check_prerequisites
    test_bluetooth
    configure_wifi
    get_camera_ip
    enable_http_server
    disable_signature_verification
    enable_telnet
    enable_rtsp
    build_firmware
    flash_firmware
    test_streaming
    display_results
}

# Run main function
main "$@"
