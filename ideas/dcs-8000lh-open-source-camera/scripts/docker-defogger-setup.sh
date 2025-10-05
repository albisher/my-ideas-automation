#!/bin/bash

# Docker-based Defogger Setup for DCS-8000LH
# Solves bluepy compilation issues on macOS

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

# Check if Docker is installed
check_docker() {
    log "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker Desktop for Mac."
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker is not running. Please start Docker Desktop."
    fi
    
    success "Docker is available and running"
}

# Build the defogger container
build_container() {
    log "Building defogger container..."
    
    if docker build -f Dockerfile.defogger -t dcs8000lh-defogger .; then
        success "Container built successfully"
    else
        error "Failed to build container"
    fi
}

# Run the defogger setup
run_defogger_setup() {
    log "Starting defogger setup in container..."
    
    echo "Starting interactive defogger setup..."
    echo "Camera MAC: $CAMERA_MAC"
    echo "Camera PIN: $CAMERA_PIN"
    echo "WiFi SSID: $WIFI_SSID"
    echo ""
    echo "The container will start with all defogger tools ready."
    echo "You can run the automated setup or use manual commands."
    echo ""
    
    # Run container with Bluetooth access
    docker run -it --rm \
        --name $CONTAINER_NAME \
        --privileged \
        --net=host \
        -v /var/run/dbus:/var/run/dbus \
        -v /dev:/dev \
        dcs8000lh-defogger \
        bash
}

# Run automated setup
run_automated_setup() {
    log "Running automated defogger setup..."
    
    docker run -it --rm \
        --name $CONTAINER_NAME \
        --privileged \
        --net=host \
        -v /var/run/dbus:/var/run/dbus \
        -v /dev:/dev \
        dcs8000lh-defogger \
        ./defogger-setup.sh
}

# Run interactive commands
run_interactive_commands() {
    log "Starting interactive defogger commands..."
    
    docker run -it --rm \
        --name $CONTAINER_NAME \
        --privileged \
        --net=host \
        -v /var/run/dbus:/var/run/dbus \
        -v /dev:/dev \
        dcs8000lh-defogger \
        ./defogger-quick-commands.sh
}

# Clean up containers
cleanup() {
    log "Cleaning up containers..."
    
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    
    success "Cleanup complete"
}

# Display help
show_help() {
    echo "DCS-8000LH Docker Defogger Setup"
    echo "================================="
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  build       - Build the defogger container"
    echo "  setup       - Run automated defogger setup"
    echo "  interactive - Run interactive defogger commands"
    echo "  shell       - Start interactive shell"
    echo "  cleanup     - Clean up containers"
    echo "  help        - Show this help"
    echo ""
    echo "Your Camera Details:"
    echo "  MAC: $CAMERA_MAC"
    echo "  PIN: $CAMERA_PIN"
    echo "  WiFi: $WIFI_SSID"
    echo ""
}

# Main function
main() {
    case "${1:-help}" in
        build)
            check_docker
            build_container
            ;;
        setup)
            check_docker
            build_container
            run_automated_setup
            ;;
        interactive)
            check_docker
            build_container
            run_interactive_commands
            ;;
        shell)
            check_docker
            build_container
            run_defogger_setup
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
