#!/usr/bin/env python3

"""
Continuous Monitor for 115200 Baud Rate
Focus on 115200 bps to capture the weird characters you're seeing
"""

import serial
import time
import sys
import os
from datetime import datetime

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
BAUD_RATE = 115200  # Focus on 115200 as you requested
TIMEOUT = 1

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def monitor_115200_continuous():
    """Continuously monitor 115200 bps for weird characters"""
    log("🔍 Continuous 115200 bps Monitor")
    log("=" * 50)
    
    log("📋 INSTRUCTIONS:")
    log("1. Keep the camera powered on")
    log("2. The script will monitor 115200 bps continuously")
    log("3. When you see weird characters, they will be captured")
    log("4. Press Ctrl+C to stop monitoring")
    log("")
    
    log("⏳ Starting continuous monitoring at 115200 bps...")
    log("💡 Power cycle the camera or press reset button to generate communication")
    
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=TIMEOUT,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        
        log("🚀 Monitoring started at 115200 bps...")
        log("💡 Try power cycling the camera or pressing reset button")
        
        character_count = 0
        session_count = 0
        
        while True:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                if data:
                    character_count += len(data)
                    session_count += 1
                    
                    log(f"📥 Session {session_count}: Captured {len(data)} characters (total: {character_count})")
                    
                    # Display raw data
                    print(f"📥 Raw data: {data}")
                    print(f"📥 Raw hex: {data.hex()}")
                    print(f"📥 Raw bytes: {[hex(b) for b in data]}")
                    
                    # Try different decoding methods
                    try:
                        decoded_utf8 = data.decode('utf-8', errors='replace')
                        print(f"📥 UTF-8: {repr(decoded_utf8)}")
                    except:
                        pass
                    
                    try:
                        decoded_ascii = data.decode('ascii', errors='replace')
                        print(f"📥 ASCII: {repr(decoded_ascii)}")
                    except:
                        pass
                    
                    try:
                        decoded_latin1 = data.decode('latin1', errors='replace')
                        print(f"📥 Latin-1: {repr(decoded_latin1)}")
                    except:
                        pass
                    
                    # Check for bootloader indicators
                    decoded_text = data.decode('utf-8', errors='ignore')
                    if any(keyword in decoded_text.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version', 'boot', 'alpha168']):
                        log("🎯 BOOTLOADER DETECTED!")
                        log("💡 Camera is in bootloader mode")
                        log("💡 You can now proceed with firmware flashing")
                        return True
                    
                    print("")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        log(f"\n⚠️ Monitoring stopped by user")
        log(f"📊 Total characters captured: {character_count}")
        log(f"📊 Total sessions: {session_count}")
        return False
    except Exception as e:
        log(f"❌ Monitoring error: {e}")
        return False
    finally:
        if 'ser' in locals():
            ser.close()
            log("🔌 USB connection closed")

def main():
    """Main function"""
    print("🔧 DCS-8000LH 115200 bps Continuous Monitor")
    print("=" * 60)
    print("Continuously monitoring 115200 bps for weird characters")
    print()
    
    success = monitor_115200_continuous()
    
    if success:
        log("✅ Bootloader communication established!")
        log("💡 You can now proceed with firmware flashing")
    else:
        log("❌ Bootloader communication not established")
        log("💡 Try power cycling the camera or pressing reset button")

if __name__ == "__main__":
    main()







