#!/usr/bin/env python3

"""
Boot Process Monitor for DCS-8000LH
Monitors the boot process for bootloader access without visual indicators
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

def monitor_boot_process(ser, duration=120):
    """Monitor camera boot process for bootloader access"""
    log(f"👁️ Monitoring boot process for {duration} seconds...")
    log("💡 Looking for boot messages, U-Boot prompt, or bootloader indicators...")
    
    start_time = time.time()
    boot_messages = ""
    bootloader_detected = False
    
    while time.time() - start_time < duration:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            text = data.decode('utf-8', errors='ignore')
            boot_messages += text
            print(f"📥 {text}", end='', flush=True)
            
            # Check for bootloader indicators
            if any(keyword in text.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version', 'boot', 'linux', 'kernel']):
                if not bootloader_detected:
                    log(f"✅ Bootloader detected!")
                    bootloader_detected = True
                    return True, boot_messages
        
        time.sleep(0.1)
    
    return False, boot_messages

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
        [b'\x03' for _ in range(30)],
        # Enter key spam
        [b'\r\n' for _ in range(30)],
        # Space key spam
        [b' ' for _ in range(30)],
        # Mixed sequence
        [b'\x03', b'\r\n', b' ', b'\t', b'\x04'] * 15
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

def main():
    """Main function"""
    print("🔧 DCS-8000LH Boot Process Monitor")
    print("=" * 60)
    print("Monitoring boot process for bootloader access")
    print("No visual indicators needed - monitoring serial output")
    print()
    
    # Instructions
    log("📋 INSTRUCTIONS:")
    log("1. Unplug the camera power")
    log("2. Wait 10 seconds")
    log("3. Press and hold the reset button (even if no indicator)")
    log("4. Plug the camera back in while holding reset button")
    log("5. Hold reset button for 5-10 seconds")
    log("6. Release reset button")
    log("7. The script will monitor for boot messages")
    log("")
    
    # Wait for user to power cycle
    log("⏳ Waiting for you to power cycle the camera...")
    log("💡 Press and hold reset button while plugging in power")
    log("💡 Hold reset button for 5-10 seconds, then release")
    log("")
    
    # Countdown
    for i in range(30, 0, -1):
        print(f"\r⏰ Starting monitoring in {i} seconds... (power cycle now)", end='', flush=True)
        time.sleep(1)
    
    print("\n")
    log("🚀 Starting boot process monitoring...")
    
    # Connect to camera
    ser = connect_to_camera()
    if not ser:
        return
    
    try:
        # Monitor boot process
        bootloader_detected, boot_messages = monitor_boot_process(ser, 120)
        
        if bootloader_detected:
            log("✅ Bootloader detected during boot process")
            
            # Try to interrupt if not already in bootloader
            if not try_boot_interrupt(ser):
                log("🔄 Trying to get into U-Boot mode...")
                if not try_boot_interrupt(ser):
                    log("❌ Could not get into U-Boot mode")
                    return
            
            log("✅ Camera is now in bootloader mode!")
            log("💡 You can now run firmware flashing commands")
            log("💡 Run: python3 auto-flash-official.py")
        else:
            log("❌ No bootloader detected during boot process")
            log("💡 Try the following:")
            log("   1. Power cycle the camera again")
            log("   2. Hold reset button longer (10-15 seconds)")
            log("   3. Try different reset button timing")
            log("   4. Check USB cable connection")
            
            if boot_messages:
                log(f"📋 Boot messages captured: {len(boot_messages)} characters")
                log("💡 Check the output above for any boot messages")
    
    except KeyboardInterrupt:
        log("⚠️ Boot monitoring interrupted by user")
    except Exception as e:
        log(f"❌ Error during boot monitoring: {e}")
    finally:
        if ser:
            ser.close()
            log("🔌 USB connection closed")

if __name__ == "__main__":
    main()







