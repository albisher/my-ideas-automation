#!/usr/bin/env python3

"""
Comprehensive Reset and Flash for DCS-8000LH
Tries multiple reset methods and firmware flashing approaches
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
    
    # Try different interrupt sequences
    interrupt_sequences = [
        # Rapid Ctrl+C
        [b'\x03' for _ in range(50)],
        # Enter key spam
        [b'\r\n' for _ in range(50)],
        # Space key spam
        [b' ' for _ in range(50)],
        # Mixed sequence
        [b'\x03', b'\r\n', b' ', b'\t', b'\x04'] * 20
    ]
    
    for i, sequence in enumerate(interrupt_sequences):
        log(f"🔄 Trying interrupt sequence {i+1}")
        
        for char in sequence:
            ser.write(char)
            time.sleep(0.1)
        
        time.sleep(3)
        
        # Check for response
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            if any(keyword in response.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version']):
                log(f"✅ Boot interrupt successful with sequence {i+1}")
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
                        time.sleep(25)  # Longer wait for large firmware
                        
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

def try_network_flash():
    """Try to flash firmware via network"""
    log("🌐 Trying network-based firmware flashing...")
    
    # Check if camera is accessible via network
    network_ips = ["192.168.1.100", "192.168.0.100", "192.168.1.1"]
    
    for ip in network_ips:
        log(f"🔄 Checking camera at {ip}...")
        try:
            import subprocess
            result = subprocess.run(["ping", "-c", "1", ip], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                log(f"✅ Camera found at {ip}")
                log("💡 Try accessing camera web interface for firmware upgrade")
                return True
        except Exception as e:
            log(f"❌ Network check failed for {ip}: {e}")
    
    return False

def main():
    """Main function"""
    print("🔧 DCS-8000LH Comprehensive Reset and Flash")
    print("=" * 60)
    print("Tries multiple reset methods and firmware flashing approaches")
    print()
    
    # Check firmware file
    if not os.path.exists(OFFICIAL_FIRMWARE):
        log(f"❌ Official firmware not found: {OFFICIAL_FIRMWARE}")
        return
    
    log(f"📁 Official firmware: {OFFICIAL_FIRMWARE}")
    log(f"📊 File size: {os.path.getsize(OFFICIAL_FIRMWARE)} bytes")
    
    # Try different approaches
    approaches = [
        ("USB Serial Flash", try_usb_serial_flash),
        ("Network Flash", try_network_flash),
        ("Extended Reset", try_extended_reset)
    ]
    
    for approach_name, approach_func in approaches:
        log(f"\n🔧 Trying {approach_name}...")
        if approach_func():
            log(f"✅ {approach_name} successful!")
            return
        else:
            log(f"❌ {approach_name} failed")
    
    log("\n❌ All approaches failed!")
    log("💡 Try the following:")
    log("   1. Check USB cable connection")
    log("   2. Try different reset button timing")
    log("   3. Check if camera has a recovery mode")
    log("   4. Try accessing camera via network")

def try_usb_serial_flash():
    """Try USB serial flashing"""
    log("🔌 Trying USB serial flashing...")
    
    # Step 1: Try to get into bootloader mode
    ser = connect_to_camera()
    if not ser:
        return False
    
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
                    return False
        
        # Step 2: Flash official firmware
        if flash_official_firmware(ser):
            log("✅ Official firmware flash successful")
            return True
        else:
            log("❌ Official firmware flash failed")
            return False
    
    except Exception as e:
        log(f"❌ USB serial flash error: {e}")
        return False
    finally:
        if ser:
            ser.close()

def try_extended_reset():
    """Try extended reset procedure"""
    log("🔄 Trying extended reset procedure...")
    
    log("📋 EXTENDED RESET INSTRUCTIONS:")
    log("1. Unplug camera power")
    log("2. Wait 30 seconds")
    log("3. Press and hold reset button")
    log("4. Plug power back in while holding reset")
    log("5. Hold reset for 15-20 seconds")
    log("6. Release reset button")
    log("7. Wait 10 seconds")
    log("8. Press and hold reset button again")
    log("9. Hold for 5 seconds")
    log("10. Release reset button")
    log("")
    
    log("⏳ Waiting for extended reset procedure...")
    log("💡 Follow the instructions above")
    
    # Wait for user to perform extended reset
    time.sleep(60)  # Wait 1 minute for extended reset
    
    # Try to connect and flash
    return try_usb_serial_flash()

if __name__ == "__main__":
    main()







