#!/usr/bin/env python3

"""
USB Device Detection for DCS-8000LH
Detect and list all available USB devices
"""

import subprocess
import os
import glob
from datetime import datetime

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def detect_usb_devices():
    """Detect all USB devices"""
    log("🔍 USB Device Detection")
    log("=" * 50)
    
    # Check for serial devices
    log("🔄 Checking for serial devices...")
    
    # Common serial device patterns
    device_patterns = [
        "/dev/cu.usb*",
        "/dev/tty.usb*", 
        "/dev/cu.usbserial*",
        "/dev/tty.usbserial*",
        "/dev/cu.*",
        "/dev/tty.*"
    ]
    
    found_devices = []
    
    for pattern in device_patterns:
        devices = glob.glob(pattern)
        if devices:
            found_devices.extend(devices)
            log(f"📱 Found devices matching {pattern}: {devices}")
    
    if found_devices:
        log(f"✅ Found {len(found_devices)} serial devices:")
        for device in found_devices:
            log(f"  📱 {device}")
    else:
        log("❌ No serial devices found")
    
    return found_devices

def check_system_profiler():
    """Check system profiler for USB devices"""
    log("\n🔍 System Profiler USB Check")
    log("=" * 50)
    
    try:
        result = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            output = result.stdout
            
            # Look for FTDI devices
            if 'FTDI' in output or 'ftdi' in output:
                log("✅ FTDI device detected in system profiler")
                lines = output.split('\n')
                for i, line in enumerate(lines):
                    if 'FTDI' in line or 'ftdi' in line:
                        log(f"📱 {line.strip()}")
                        # Show context
                        for j in range(max(0, i-2), min(len(lines), i+3)):
                            if j != i:
                                log(f"   {lines[j].strip()}")
            else:
                log("❌ No FTDI device found in system profiler")
            
            # Look for serial devices
            if 'Serial' in output or 'serial' in output:
                log("✅ Serial device detected in system profiler")
                lines = output.split('\n')
                for i, line in enumerate(lines):
                    if 'Serial' in line or 'serial' in line:
                        log(f"📱 {line.strip()}")
            else:
                log("❌ No serial device found in system profiler")
                
        else:
            log(f"❌ system_profiler failed: {result.stderr}")
            
    except Exception as e:
        log(f"❌ System profiler check failed: {e}")

def check_camera_connection():
    """Check if camera is connected via network"""
    log("\n🔍 Camera Network Check")
    log("=" * 50)
    
    # Common camera IP addresses
    camera_ips = [
        "192.168.1.100",
        "192.168.1.101", 
        "192.168.1.102",
        "192.168.0.100",
        "192.168.0.101",
        "192.168.2.37",  # From defogger docs
        "10.0.0.100"
    ]
    
    for ip in camera_ips:
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '1000', ip], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                log(f"✅ Camera found at {ip}")
                return ip
        except:
            pass
    
    log("❌ No camera found on network")
    return None

def main():
    """Main function"""
    print("🔧 DCS-8000LH USB Device Detection")
    print("=" * 60)
    print("Detecting USB devices and camera connection")
    print()
    
    # Step 1: Detect USB devices
    devices = detect_usb_devices()
    
    # Step 2: Check system profiler
    check_system_profiler()
    
    # Step 3: Check camera network connection
    camera_ip = check_camera_connection()
    
    # Summary
    log(f"\n{'='*60}")
    log("📊 SUMMARY")
    log("=" * 60)
    
    if devices:
        log(f"✅ Found {len(devices)} USB serial devices")
        log("💡 Try connecting to the camera using one of these devices")
    else:
        log("❌ No USB serial devices found")
        log("💡 Check if FTDI adapter is connected")
        log("💡 Check if camera is powered on")
        log("💡 Check wiring connections")
    
    if camera_ip:
        log(f"✅ Camera found on network at {camera_ip}")
        log("💡 Camera is powered on and connected")
    else:
        log("❌ Camera not found on network")
        log("💡 Camera may not be powered on")
        log("💡 Camera may not be connected to network")
    
    # Recommendations
    log(f"\n{'='*60}")
    log("💡 RECOMMENDATIONS")
    log("=" * 60)
    
    if not devices and not camera_ip:
        log("🔧 TROUBLESHOOTING STEPS:")
        log("1. Check if FTDI adapter is connected to computer")
        log("2. Check if camera is powered on")
        log("3. Check wiring connections (VCC, TX, RX, GND)")
        log("4. Try different USB port")
        log("5. Check FTDI driver installation")
    elif devices and not camera_ip:
        log("✅ USB connection available")
        log("💡 Proceed with serial communication tests")
    elif not devices and camera_ip:
        log("✅ Camera is powered on")
        log("💡 Check USB serial connection")
    else:
        log("✅ Both USB and network connections available")
        log("💡 Proceed with firmware flashing")

if __name__ == "__main__":
    main()







