#!/bin/bash

# Non-interactive Defogger Commands Runner
# Runs defogger commands in Docker container without TTY

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CAMERA_MAC="B0:C5:54:51:EB:76"
CAMERA_PIN="052446"
WIFI_SSID="SA"
WIFI_PASSWORD="62Dad64Mom"
CONTAINER_NAME="dcs8000lh-defogger"

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

# Run defogger commands in container
run_defogger_commands() {
    log "Running defogger commands in Docker container..."
    
    # Test Bluetooth connection
    log "Testing Bluetooth connection to camera..."
    docker run --rm \
        --privileged \
        --net=host \
        -v /var/run/dbus:/var/run/dbus \
        -v /dev:/dev \
        dcs8000lh-defogger \
        python3 dcs8000lh-configure.py $CAMERA_MAC $CAMERA_PIN --survey || warning "Bluetooth connection failed - camera may not be in pairing mode"
    
    # Configure WiFi
    log "Configuring WiFi settings..."
    docker run --rm \
        --privileged \
        --net=host \
        -v /var/run/dbus:/var/run/dbus \
        -v /dev:/dev \
        dcs8000lh-defogger \
        python3 dcs8000lh-configure.py $CAMERA_MAC $CAMERA_PIN --essid "$WIFI_SSID" --wifipw "$WIFI_PASSWORD" || warning "WiFi configuration failed"
    
    # Enable services
    log "Enabling camera services..."
    
    # Enable HTTP server
    docker run --rm \
        --privileged \
        --net=host \
        -v /var/run/dbus:/var/run/dbus \
        -v /dev:/dev \
        dcs8000lh-defogger \
        python3 dcs8000lh-configure.py $CAMERA_MAC $CAMERA_PIN --lighttpd || warning "HTTP server enable failed"
    
    # Enable unsigned firmware
    docker run --rm \
        --privileged \
        --net=host \
        -v /var/run/dbus:/var/run/dbus \
        -v /dev:/dev \
        dcs8000lh-defogger \
        python3 dcs8000lh-configure.py $CAMERA_MAC $CAMERA_PIN --unsignedfw || warning "Unsigned firmware enable failed"
    
    # Enable telnet
    docker run --rm \
        --privileged \
        --net=host \
        -v /var/run/dbus:/var/run/dbus \
        -v /dev:/dev \
        dcs8000lh-defogger \
        python3 dcs8000lh-configure.py $CAMERA_MAC $CAMERA_PIN --telnetd || warning "Telnet enable failed"
    
    # Enable RTSP
    docker run --rm \
        --privileged \
        --net=host \
        -v /var/run/dbus:/var/run/dbus \
        -v /dev:/dev \
        dcs8000lh-defogger \
        python3 dcs8000lh-configure.py $CAMERA_MAC $CAMERA_PIN --rtsp || warning "RTSP enable failed"
    
    success "Defogger commands completed"
}

# Build and flash firmware
build_and_flash_firmware() {
    log "Building and flashing custom firmware..."
    
    # Build firmware
    docker run --rm \
        --privileged \
        --net=host \
        -v /var/run/dbus:/var/run/dbus \
        -v /dev:/dev \
        dcs8000lh-defogger \
        make || error "Firmware build failed"
    
    success "Firmware built successfully"
    
    # Note: Firmware flashing requires camera IP which we'll detect
    log "Firmware ready for flashing. Camera IP will be detected automatically."
}

# Detect camera IP
detect_camera_ip() {
    log "Detecting camera IP address..."
    
    # Try to find camera on network
    CAMERA_IP=$(docker run --rm \
        --privileged \
        --net=host \
        dcs8000lh-defogger \
        bash -c "
            # Scan for camera
            for ip in 192.168.1.{1..254} 192.168.0.{1..254} 192.168.68.{1..254}; do
                if ping -c 1 -W 1 \$ip >/dev/null 2>&1; then
                    # Check if it's our camera
                    if curl -s --connect-timeout 2 http://\$ip/common/info.cgi | grep -q 'SHIP'; then
                        echo \$ip
                        exit 0
                    fi
                fi
            done
            echo 'NOT_FOUND'
        ")
    
    if [ "$CAMERA_IP" != "NOT_FOUND" ]; then
        success "Camera found at IP: $CAMERA_IP"
        echo "CAMERA_IP=$CAMERA_IP" > camera_ip.txt
    else
        warning "Camera IP not detected automatically"
        echo "Please manually set camera IP in camera_ip.txt"
    fi
}

# Flash firmware to camera
flash_firmware() {
    if [ -f "camera_ip.txt" ]; then
        source camera_ip.txt
        if [ -n "$CAMERA_IP" ]; then
            log "Flashing firmware to camera at $CAMERA_IP..."
            
            docker run --rm \
                --privileged \
                --net=host \
                dcs8000lh-defogger \
                bash -c "
                    curl --http1.0 -u admin:$CAMERA_PIN --form upload=@fw.tar http://$CAMERA_IP/config/firmwareupgrade.cgi
                    echo 'Firmware upload completed'
                " || warning "Firmware flashing failed"
        else
            warning "Camera IP not set. Please set CAMERA_IP in camera_ip.txt"
        fi
    else
        warning "Camera IP file not found. Run detect_camera_ip first."
    fi
}

# Test streaming
test_streaming() {
    if [ -f "camera_ip.txt" ]; then
        source camera_ip.txt
        if [ -n "$CAMERA_IP" ]; then
            log "Testing camera streaming..."
            
            # Test HTTP streaming
            log "Testing HTTP streaming at http://$CAMERA_IP/video/mpegts.cgi"
            docker run --rm \
                --privileged \
                --net=host \
                dcs8000lh-defogger \
                curl -I http://$CAMERA_IP/video/mpegts.cgi || warning "HTTP streaming test failed"
            
            # Test RTSP streaming
            log "Testing RTSP streaming at rtsp://$CAMERA_IP/live/profile.0"
            docker run --rm \
                --privileged \
                --net=host \
                dcs8000lh-defogger \
                timeout 5 ffmpeg -i rtsp://$CAMERA_IP/live/profile.0 -f null - 2>/dev/null || warning "RTSP streaming test failed"
            
            success "Streaming tests completed"
        else
            warning "Camera IP not set. Please set CAMERA_IP in camera_ip.txt"
        fi
    else
        warning "Camera IP file not found. Run detect_camera_ip first."
    fi
}

# Main menu
show_menu() {
    echo "DCS-8000LH Defogger Commands"
    echo "============================"
    echo ""
    echo "Your Camera Details:"
    echo "  MAC: $CAMERA_MAC"
    echo "  PIN: $CAMERA_PIN"
    echo "  WiFi: $WIFI_SSID"
    echo ""
    echo "Available Commands:"
    echo "  1. Run defogger commands"
    echo "  2. Build firmware"
    echo "  3. Detect camera IP"
    echo "  4. Flash firmware"
    echo "  5. Test streaming"
    echo "  6. Run all steps"
    echo "  0. Exit"
    echo ""
}

# Run all steps
run_all_steps() {
    log "Running complete defogger setup..."
    
    run_defogger_commands
    build_and_flash_firmware
    detect_camera_ip
    flash_firmware
    test_streaming
    
    success "Complete defogger setup finished!"
}

# Main function
main() {
    case "${1:-menu}" in
        commands)
            run_defogger_commands
            ;;
        build)
            build_and_flash_firmware
            ;;
        detect)
            detect_camera_ip
            ;;
        flash)
            flash_firmware
            ;;
        test)
            test_streaming
            ;;
        all)
            run_all_steps
            ;;
        menu)
            show_menu
            ;;
        *)
            echo "Usage: $0 [commands|build|detect|flash|test|all|menu]"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
