#!/usr/bin/env python3

"""
USB Bootloader Mode Script for DCS-8000LH
This script helps get the camera into U-Boot mode for firmware flashing
"""

import serial
import time
import sys
import os
from datetime import datetime

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
BAUD_RATE = 115200
TIMEOUT = 1

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def connect_to_camera():
    """Connect to camera via USB serial"""
    try:
        log("🔌 Connecting to camera...")
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=TIMEOUT,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        log(f"✅ Connected to {SERIAL_PORT}")
        return ser
    except Exception as e:
        log(f"❌ Connection failed: {e}")
        return None

def send_command(ser, command, wait_time=1):
    """Send command and get response"""
    try:
        log(f"📤 Sending: {command}")
        ser.write(f"{command}\r\n".encode())
        ser.flush()
        time.sleep(wait_time)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            if response.strip():
                log(f"📥 Response: {response.strip()}")
                return response.strip()
        
        return None
    except Exception as e:
        log(f"❌ Command failed: {e}")
        return None

def try_boot_interrupt_sequence(ser):
    """Try comprehensive boot interrupt sequence"""
    log("🔄 Starting comprehensive boot interrupt sequence...")
    
    # Clear buffers
    ser.flushInput()
    ser.flushOutput()
    time.sleep(0.5)
    
    # Method 1: Rapid Ctrl+C sequence
    log("🔄 Method 1: Rapid Ctrl+C sequence")
    for i in range(20):
        ser.write(b'\x03')
        time.sleep(0.1)
    
    time.sleep(2)
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if any(keyword in response.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help']):
            log("✅ Boot interrupt successful with Ctrl+C")
            return True
    
    # Method 2: Enter key sequence
    log("🔄 Method 2: Enter key sequence")
    for i in range(20):
        ser.write(b'\r\n')
        time.sleep(0.1)
    
    time.sleep(2)
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if any(keyword in response.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help']):
            log("✅ Boot interrupt successful with Enter keys")
            return True
    
    # Method 3: Space key sequence
    log("🔄 Method 3: Space key sequence")
    for i in range(20):
        ser.write(b' ')
        time.sleep(0.1)
    
    time.sleep(2)
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if any(keyword in response.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help']):
            log("✅ Boot interrupt successful with Space keys")
            return True
    
    # Method 4: Tab key sequence
    log("🔄 Method 4: Tab key sequence")
    for i in range(20):
        ser.write(b'\t')
        time.sleep(0.1)
    
    time.sleep(2)
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if any(keyword in response.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help']):
            log("✅ Boot interrupt successful with Tab keys")
            return True
    
    # Method 5: Mixed sequence
    log("🔄 Method 5: Mixed sequence")
    sequence = [b'\x03', b'\r\n', b' ', b'\t', b'\x04']
    for _ in range(10):
        for char in sequence:
            ser.write(char)
            time.sleep(0.1)
    
    time.sleep(2)
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if any(keyword in response.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help']):
            log("✅ Boot interrupt successful with mixed sequence")
            return True
    
    return False

def try_different_baud_rates():
    """Try different baud rates to find working one"""
    log("🔄 Trying different baud rates...")
    
    baud_rates = [57600, 115200, 38400, 19200, 9600, 230400]
    
    for baud in baud_rates:
        try:
            log(f"🔄 Trying baud rate: {baud}")
            ser = serial.Serial(
                port=SERIAL_PORT,
                baudrate=baud,
                timeout=TIMEOUT
            )
            
            # Try boot interrupt
            if try_boot_interrupt_sequence(ser):
                log(f"✅ Success with baud rate: {baud}")
                return ser
            
            ser.close()
        except Exception as e:
            log(f"❌ Failed with baud rate {baud}: {e}")
    
    return None

def test_uboot_commands(ser):
    """Test if we're in U-Boot mode"""
    log("🔍 Testing U-Boot commands...")
    
    uboot_commands = [
        "help",
        "version",
        "printenv",
        "bdinfo",
        "md 0x80000000 10"
    ]
    
    for cmd in uboot_commands:
        response = send_command(ser, cmd, 2)
        if response and any(keyword in response.lower() for keyword in ['uboot', 'version', 'help', 'memory', 'environment']):
            log(f"✅ U-Boot mode confirmed with: {cmd}")
            return True
    
    return False

def main():
    """Main function"""
    print("🔧 DCS-8000LH USB Bootloader Mode")
    print("=" * 50)
    print("This script will help get the camera into U-Boot mode")
    print("for firmware flashing.")
    print()
    
    # Step 1: Try default baud rate
    ser = connect_to_camera()
    if not ser:
        return
    
    try:
        # Step 2: Try boot interrupt
        if try_boot_interrupt_sequence(ser):
            log("✅ Boot interrupt successful")
            
            # Step 3: Test U-Boot commands
            if test_uboot_commands(ser):
                log("✅ Camera is now in U-Boot mode!")
                log("💡 You can now run firmware flashing commands")
                return
            else:
                log("❌ Not in U-Boot mode")
        else:
            log("❌ Boot interrupt failed with default baud rate")
            
            # Step 4: Try different baud rates
            ser.close()
            ser = try_different_baud_rates()
            
            if ser:
                if test_uboot_commands(ser):
                    log("✅ Camera is now in U-Boot mode!")
                    log("💡 You can now run firmware flashing commands")
                    return
                else:
                    log("❌ Still not in U-Boot mode")
            else:
                log("❌ No working baud rate found")
        
        log("❌ Could not get camera into U-Boot mode")
        log("💡 Try the following:")
        log("   1. Power cycle the camera")
        log("   2. Press and hold reset button while powering on")
        log("   3. Check if camera has a recovery mode")
        log("   4. Try different USB cable or port")
        
    except KeyboardInterrupt:
        log("⚠️ Interrupted by user")
    except Exception as e:
        log(f"❌ Error: {e}")
    finally:
        if ser:
            ser.close()
            log("🔌 Connection closed")

if __name__ == "__main__":
    main()

