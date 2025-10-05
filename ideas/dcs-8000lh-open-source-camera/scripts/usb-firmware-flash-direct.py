#!/usr/bin/env python3

"""
Direct USB Firmware Flashing Script for DCS-8000LH
Simplified approach focusing on getting camera into bootloader mode
"""

import serial
import time
import sys
import os
from datetime import datetime

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
BAUD_RATE = 115200
TIMEOUT = 2
FIRMWARE_FILE = "/Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts/fw.tar"

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
        
        log("📥 No response")
        return None
    except Exception as e:
        log(f"❌ Command failed: {e}")
        return None

def try_boot_interrupt(ser):
    """Try to interrupt boot process"""
    log("🔄 Attempting boot interrupt...")
    
    # Clear buffers
    ser.flushInput()
    ser.flushOutput()
    
    # Try different interrupt methods
    interrupt_methods = [
        # Method 1: Multiple Ctrl+C
        lambda: [ser.write(b'\x03') for _ in range(5)],
        
        # Method 2: Enter key spam
        lambda: [ser.write(b'\r\n') for _ in range(10)],
        
        # Method 3: Space key spam  
        lambda: [ser.write(b' ') for _ in range(10)],
        
        # Method 4: Tab key spam
        lambda: [ser.write(b'\t') for _ in range(10)],
    ]
    
    for i, method in enumerate(interrupt_methods):
        log(f"🔄 Trying interrupt method {i+1}")
        method()
        time.sleep(2)
        
        # Check for response
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            if any(keyword in response.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version']):
                log(f"✅ Boot interrupt successful with method {i+1}")
                return True
    
    return False

def try_direct_commands(ser):
    """Try direct commands to see if camera responds"""
    log("🔄 Trying direct commands...")
    
    commands = [
        "help",
        "version", 
        "printenv",
        "bdinfo",
        "md 0x80000000 10",
        "mw 0x80000000 0x12345678",
        "md 0x80000000 10"
    ]
    
    for cmd in commands:
        response = send_command(ser, cmd, 2)
        if response and any(keyword in response.lower() for keyword in ['uboot', 'version', 'help', 'memory', '12345678']):
            log(f"✅ Camera responding to: {cmd}")
            return True
    
    return False

def try_firmware_upload(ser):
    """Try to upload firmware"""
    log("📤 Attempting firmware upload...")
    
    if not os.path.exists(FIRMWARE_FILE):
        log(f"❌ Firmware not found: {FIRMWARE_FILE}")
        return False
    
    log(f"📁 Firmware: {FIRMWARE_FILE} ({os.path.getsize(FIRMWARE_FILE)} bytes)")
    
    # Try different upload commands
    upload_commands = [
        "loadb 0x80000000",
        "loads 0x80000000", 
        "loadx 0x80000000",
        "loady 0x80000000",
        "loadz 0x80000000"
    ]
    
    for cmd in upload_commands:
        log(f"🔄 Trying: {cmd}")
        response = send_command(ser, cmd, 3)
        
        if response and "ready" in response.lower():
            log(f"✅ Upload ready: {response}")
            
            # Send firmware
            try:
                with open(FIRMWARE_FILE, 'rb') as f:
                    data = f.read()
                    log(f"📤 Sending {len(data)} bytes...")
                    ser.write(data)
                    time.sleep(3)
                    
                    # Check response
                    if ser.in_waiting > 0:
                        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                        log(f"📥 Upload response: {response}")
                        
                        # Try to flash
                        flash_commands = [
                            "erase 0x9f000000 +0x100000",
                            "cp.b 0x80000000 0x9f000000 0x100000", 
                            "protect on 0x9f000000 +0x100000"
                        ]
                        
                        for flash_cmd in flash_commands:
                            send_command(ser, flash_cmd, 3)
                        
                        return True
            except Exception as e:
                log(f"❌ Upload failed: {e}")
    
    return False

def main():
    """Main function"""
    print("🔧 DCS-8000LH Direct USB Firmware Flash")
    print("=" * 50)
    print(f"Port: {SERIAL_PORT}")
    print(f"Firmware: {FIRMWARE_FILE}")
    print()
    
    # Check firmware
    if not os.path.exists(FIRMWARE_FILE):
        log(f"❌ Firmware not found: {FIRMWARE_FILE}")
        return
    
    # Connect
    ser = connect_to_camera()
    if not ser:
        return
    
    try:
        # Step 1: Try boot interrupt
        if try_boot_interrupt(ser):
            log("✅ Boot interrupt successful")
            
            # Step 2: Try direct commands
            if try_direct_commands(ser):
                log("✅ Camera responding to commands")
                
                # Step 3: Try firmware upload
                if try_firmware_upload(ser):
                    log("✅ Firmware upload successful!")
                else:
                    log("❌ Firmware upload failed")
            else:
                log("❌ Camera not responding to commands")
        else:
            log("❌ Boot interrupt failed")
            log("💡 Try power cycling the camera and running again")
        
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

