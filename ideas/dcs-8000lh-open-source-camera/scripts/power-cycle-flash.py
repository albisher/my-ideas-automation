#!/usr/bin/env python3

"""
Power Cycle Firmware Flash for DCS-8000LH
Handles power cycling and firmware flashing process
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
OFFICIAL_FIRMWARE = "/Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts/DCS-8000LH_Ax_v2.02.02_3014.bin"

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

def monitor_boot_process(ser, duration=60):
    """Monitor camera boot process for bootloader access"""
    log(f"👁️ Monitoring boot process for {duration} seconds...")
    
    start_time = time.time()
    boot_messages = ""
    
    while time.time() - start_time < duration:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            text = data.decode('utf-8', errors='ignore')
            boot_messages += text
            print(f"📥 {text}", end='', flush=True)
            
            # Check for bootloader indicators
            if any(keyword in text.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version', 'boot']):
                log(f"✅ Bootloader detected!")
                return True, boot_messages
        
        time.sleep(0.1)
    
    return False, boot_messages

def try_boot_interrupt_during_boot(ser):
    """Try to interrupt boot process during monitoring"""
    log("🔄 Attempting boot interrupt during boot process...")
    
    # Try different interrupt sequences
    interrupt_sequences = [
        # Rapid Ctrl+C
        [b'\x03' for _ in range(20)],
        # Enter key spam
        [b'\r\n' for _ in range(20)],
        # Space key spam
        [b' ' for _ in range(20)],
        # Mixed sequence
        [b'\x03', b'\r\n', b' ', b'\t', b'\x04'] * 10
    ]
    
    for i, sequence in enumerate(interrupt_sequences):
        log(f"🔄 Trying interrupt sequence {i+1}")
        
        for char in sequence:
            ser.write(char)
            time.sleep(0.1)
        
        time.sleep(2)
        
        # Check for response
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            if any(keyword in response.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version']):
                log(f"✅ Boot interrupt successful with sequence {i+1}")
                log(f"📥 Response: {response}")
                return True
    
    return False

def flash_firmware(ser):
    """Flash the official firmware"""
    log("📤 Flashing official D-Link firmware...")
    
    if not os.path.exists(OFFICIAL_FIRMWARE):
        log(f"❌ Official firmware not found: {OFFICIAL_FIRMWARE}")
        return False
    
    file_size = os.path.getsize(OFFICIAL_FIRMWARE)
    log(f"📊 Firmware size: {file_size} bytes")
    
    # Try different upload methods
    upload_commands = [
        "loadb 0x80000000",
        "loads 0x80000000",
        "loadx 0x80000000",
        "loady 0x80000000",
        "loadz 0x80000000"
    ]
    
    for cmd in upload_commands:
        log(f"🔄 Trying upload command: {cmd}")
        
        try:
            # Send command
            ser.write(f"{cmd}\r\n".encode())
            ser.flush()
            time.sleep(2)
            
            # Check for ready response
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                if "ready" in response.lower():
                    log(f"✅ Upload command ready: {response}")
                    
                    # Send firmware data
                    with open(OFFICIAL_FIRMWARE, 'rb') as f:
                        data = f.read()
                        log(f"📤 Sending {len(data)} bytes of official firmware...")
                        ser.write(data)
                        time.sleep(15)  # Longer wait for large firmware
                        
                        # Check upload response
                        if ser.in_waiting > 0:
                            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                            log(f"📥 Upload response: {response}")
                            
                            # Try to flash to flash memory
                            flash_commands = [
                                "erase 0x9f000000 +0x1000000",
                                "cp.b 0x80000000 0x9f000000 0x1000000",
                                "protect on 0x9f000000 +0x1000000"
                            ]
                            
                            for flash_cmd in flash_commands:
                                log(f"🔄 Executing: {flash_cmd}")
                                ser.write(f"{flash_cmd}\r\n".encode())
                                ser.flush()
                                time.sleep(5)
                                
                                if ser.in_waiting > 0:
                                    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                                    log(f"📥 Flash response: {response}")
                            
                            return True
                else:
                    log(f"📥 Command response: {response}")
            
        except Exception as e:
            log(f"❌ Upload command failed: {e}")
    
    return False

def main():
    """Main function"""
    print("🔧 DCS-8000LH Power Cycle Firmware Flash")
    print("=" * 60)
    print("Power cycle the camera to get into bootloader mode")
    print()
    
    # Check firmware file
    if not os.path.exists(OFFICIAL_FIRMWARE):
        log(f"❌ Official firmware not found: {OFFICIAL_FIRMWARE}")
        return
    
    log(f"📁 Official firmware: {OFFICIAL_FIRMWARE}")
    log(f"📊 File size: {os.path.getsize(OFFICIAL_FIRMWARE)} bytes")
    
    # Instructions for user
    log("📋 INSTRUCTIONS:")
    log("1. Unplug the camera power")
    log("2. Wait 10 seconds")
    log("3. Plug the camera back in")
    log("4. The script will monitor for bootloader access")
    log("")
    
    input("Press Enter when you have power cycled the camera...")
    
    # Connect to camera
    ser = connect_to_camera()
    if not ser:
        return
    
    try:
        # Monitor boot process
        bootloader_detected, boot_messages = monitor_boot_process(ser, 60)
        
        if bootloader_detected:
            log("✅ Bootloader detected during boot process")
            
            # Try to interrupt if not already in bootloader
            if not try_boot_interrupt_during_boot(ser):
                log("🔄 Trying to get into U-Boot mode...")
                if not try_boot_interrupt_during_boot(ser):
                    log("❌ Could not get into U-Boot mode")
                    return
            
            # Flash firmware
            if flash_firmware(ser):
                log("✅ Official firmware flash successful")
                log("🎯 Official D-Link firmware has been flashed successfully!")
                log("💡 Camera should now be running the official firmware")
            else:
                log("❌ Official firmware flash failed")
        else:
            log("❌ No bootloader detected during boot process")
            log("💡 Try the following:")
            log("   1. Power cycle the camera again")
            log("   2. Press and hold reset button while powering on")
            log("   3. Check USB cable connection")
    
    except KeyboardInterrupt:
        log("⚠️ Firmware flash interrupted by user")
    except Exception as e:
        log(f"❌ Error during firmware flash: {e}")
    finally:
        if ser:
            ser.close()
            log("🔌 USB connection closed")

if __name__ == "__main__":
    main()







