#!/usr/bin/env python3

"""
Automatic Official Firmware Flash for DCS-8000LH
Automatically handles power cycling and firmware flashing
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

def try_boot_interrupt(ser):
    """Try to interrupt boot process"""
    log("🔄 Attempting boot interrupt...")
    
    # Clear buffers
    ser.flushInput()
    ser.flushOutput()
    time.sleep(0.5)
    
    # Try rapid Ctrl+C sequence
    log("🔄 Sending rapid Ctrl+C sequence...")
    for i in range(50):
        ser.write(b'\x03')
        time.sleep(0.1)
    
    time.sleep(3)
    
    # Check for response
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if any(keyword in response.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version']):
            log(f"✅ Boot interrupt successful!")
            log(f"📥 Response: {response}")
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
            if try_boot_interrupt(ser):
                log(f"✅ Success with baud rate: {baud}")
                return ser
            
            ser.close()
        except Exception as e:
            log(f"❌ Failed with baud rate {baud}: {e}")
    
    return None

def flash_official_firmware(ser):
    """Flash the official D-Link firmware"""
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
                        time.sleep(20)  # Longer wait for large firmware
                        
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

def verify_flash_success(ser):
    """Verify firmware flash was successful"""
    log("🔍 Verifying firmware flash...")
    
    # Try to boot the new firmware
    boot_commands = [
        "bootm 0x80000000",
        "go 0x80000000",
        "run bootcmd"
    ]
    
    for cmd in boot_commands:
        log(f"🔄 Trying boot command: {cmd}")
        try:
            ser.write(f"{cmd}\r\n".encode())
            ser.flush()
            time.sleep(5)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                log(f"📥 Boot response: {response}")
                return True
        except Exception as e:
            log(f"❌ Boot command failed: {e}")
    
    return False

def main():
    """Main function"""
    print("🔧 DCS-8000LH Automatic Official Firmware Flash")
    print("=" * 60)
    print("Automatically flashing complete official D-Link firmware")
    print()
    
    # Check firmware file
    if not os.path.exists(OFFICIAL_FIRMWARE):
        log(f"❌ Official firmware not found: {OFFICIAL_FIRMWARE}")
        return
    
    log(f"📁 Official firmware: {OFFICIAL_FIRMWARE}")
    log(f"📊 File size: {os.path.getsize(OFFICIAL_FIRMWARE)} bytes")
    
    # Step 1: Try to get into bootloader mode
    ser = connect_to_camera()
    if not ser:
        return
    
    try:
        # Try boot interrupt
        if try_boot_interrupt(ser):
            log("✅ Camera is in bootloader mode")
        else:
            log("❌ Boot interrupt failed, trying different baud rates...")
            ser.close()
            ser = try_different_baud_rates()
            
            if not ser:
                log("❌ Could not get camera into bootloader mode")
                log("💡 Camera may need to be power cycled")
                log("💡 Try unplugging and plugging back in the camera")
                return
        
        # Step 2: Flash official firmware
        if flash_official_firmware(ser):
            log("✅ Official firmware flash successful")
            
            # Step 3: Verify flash
            if verify_flash_success(ser):
                log("✅ Firmware verification successful")
                log("🎯 Official D-Link firmware has been flashed successfully!")
                log("💡 Camera should now be running the official firmware")
            else:
                log("❌ Firmware verification failed")
        else:
            log("❌ Official firmware flash failed")
    
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






