#!/usr/bin/env python3

"""
Complete Firmware Flashing Script for DCS-8000LH
This script handles firmware flashing using all available methods
"""

import os
import sys
import time
import subprocess
from datetime import datetime

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_firmware_files():
    """Check available firmware files"""
    log("🔍 Checking firmware files...")
    
    firmware_files = [
        ("fw.tar", "Custom defogger firmware"),
        ("DCS-8000LH_Ax_v2.02.02_3014.bin", "Original D-Link firmware"),
        ("update.bin", "Update script"),
        ("update.bin.aes", "Encrypted update script")
    ]
    
    available = []
    for filename, description in firmware_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            log(f"✅ {description}: {filename} ({size} bytes)")
            available.append((filename, description, size))
        else:
            log(f"❌ {description} not found: {filename}")
    
    return available

def check_usb_connection():
    """Check USB connection"""
    log("🔌 Checking USB connection...")
    
    usb_devices = [
        "/dev/cu.usbserial-31120",
        "/dev/ttyUSB0",
        "/dev/ttyACM0"
    ]
    
    for device in usb_devices:
        if os.path.exists(device):
            log(f"✅ USB device found: {device}")
            return device
    
    log("❌ No USB device found")
    return None

def run_defogger_setup():
    """Run the defogger setup using available tools"""
    log("🔧 Running defogger setup...")
    
    # Check if we have the defogger tools
    if os.path.exists("defogger-setup.sh"):
        log("✅ Found defogger-setup.sh")
        try:
            result = subprocess.run(["./defogger-setup.sh"], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                log("✅ Defogger setup completed successfully")
                return True
            else:
                log(f"❌ Defogger setup failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            log("❌ Defogger setup timed out")
            return False
        except Exception as e:
            log(f"❌ Defogger setup error: {e}")
            return False
    else:
        log("❌ defogger-setup.sh not found")
        return False

def run_docker_defogger():
    """Run defogger using Docker container"""
    log("🐳 Running defogger via Docker...")
    
    try:
        # Build the container if needed
        log("🔨 Building Docker container...")
        build_result = subprocess.run([
            "docker", "build", "-f", "Dockerfile.defogger", 
            "-t", "dcs8000lh-defogger", "."
        ], capture_output=True, text=True, timeout=300)
        
        if build_result.returncode != 0:
            log(f"❌ Docker build failed: {build_result.stderr}")
            return False
        
        log("✅ Docker container built successfully")
        
        # Run the defogger setup in container
        log("🚀 Running defogger setup in container...")
        run_result = subprocess.run([
            "docker", "run", "--rm", "--privileged", "--net=host",
            "-v", "/var/run/dbus:/var/run/dbus", "-v", "/dev:/dev",
            "dcs8000lh-defogger", "./defogger-setup.sh"
        ], capture_output=True, text=True, timeout=600)
        
        if run_result.returncode == 0:
            log("✅ Docker defogger setup completed successfully")
            return True
        else:
            log(f"❌ Docker defogger setup failed: {run_result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        log("❌ Docker defogger setup timed out")
        return False
    except Exception as e:
        log(f"❌ Docker defogger setup error: {e}")
        return False

def run_manual_firmware_flash():
    """Run manual firmware flashing"""
    log("🔧 Running manual firmware flashing...")
    
    # Check if we have firmware files
    firmware_files = check_firmware_files()
    if not firmware_files:
        log("❌ No firmware files available")
        return False
    
    # Use the first available firmware
    firmware_file, description, size = firmware_files[0]
    log(f"📁 Using firmware: {firmware_file} ({description})")
    
    # Try different flashing methods
    methods = [
        ("USB Serial Flash", f"python3 usb-firmware-flash-final.py"),
        ("USB Direct Flash", f"python3 usb-firmware-flash-direct.py"),
        ("USB Bootloader Mode", f"python3 usb-bootloader-mode.py")
    ]
    
    for method_name, command in methods:
        log(f"🔄 Trying {method_name}...")
        try:
            result = subprocess.run(command.split(), 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                log(f"✅ {method_name} completed successfully")
                return True
            else:
                log(f"❌ {method_name} failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            log(f"❌ {method_name} timed out")
        except Exception as e:
            log(f"❌ {method_name} error: {e}")
    
    return False

def verify_camera_functionality():
    """Verify camera is working after firmware flash"""
    log("🔍 Verifying camera functionality...")
    
    # Check if camera is accessible via network
    network_checks = [
        ("Ping 192.168.1.100", "ping -c 3 192.168.1.100"),
        ("Ping 192.168.1.1", "ping -c 3 192.168.1.1"),
        ("Check HTTP", "curl -I http://192.168.1.100"),
        ("Check HTTPS", "curl -I https://192.168.1.100")
    ]
    
    for check_name, command in network_checks:
        try:
            result = subprocess.run(command.split(), 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                log(f"✅ {check_name} successful")
            else:
                log(f"❌ {check_name} failed")
        except Exception as e:
            log(f"❌ {check_name} error: {e}")
    
    return True

def main():
    """Main function"""
    print("🔧 DCS-8000LH Complete Firmware Flash")
    print("=" * 60)
    print("Comprehensive firmware flashing using all available methods")
    print()
    
    # Step 1: Check prerequisites
    log("📋 Checking prerequisites...")
    
    # Check firmware files
    firmware_files = check_firmware_files()
    if not firmware_files:
        log("❌ No firmware files available")
        log("💡 Please ensure firmware files are present")
        return
    
    # Check USB connection
    usb_device = check_usb_connection()
    if not usb_device:
        log("❌ No USB device found")
        log("💡 Please check USB connection")
        return
    
    log("✅ Prerequisites check passed")
    
    # Step 2: Try different flashing methods
    log("\n🔄 Attempting firmware flashing...")
    
    methods = [
        ("Docker Defogger", run_docker_defogger),
        ("Manual Firmware Flash", run_manual_firmware_flash),
        ("Defogger Setup", run_defogger_setup)
    ]
    
    success = False
    for method_name, method_func in methods:
        log(f"\n🔧 Trying {method_name}...")
        if method_func():
            log(f"✅ {method_name} successful!")
            success = True
            break
        else:
            log(f"❌ {method_name} failed")
    
    if success:
        log("\n🎯 Firmware flashing completed successfully!")
        
        # Step 3: Verify functionality
        log("\n🔍 Verifying camera functionality...")
        verify_camera_functionality()
        
        log("\n✅ Camera firmware has been flashed successfully!")
        log("💡 Camera should now be accessible and functional")
        log("🔍 Check camera status and test streaming")
    else:
        log("\n❌ All firmware flashing methods failed!")
        log("💡 Try the following:")
        log("   1. Check USB connection")
        log("   2. Power cycle the camera")
        log("   3. Check firmware files")
        log("   4. Try manual recovery procedures")

if __name__ == "__main__":
    main()






