#!/usr/bin/env python3

"""
Capture Garbled Characters for DCS-8000LH
Continuously monitor and capture the weird characters you're seeing
"""

import serial
import time
import sys
import os
from datetime import datetime

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
BAUD_RATE = 115200  # Based on your observation of weird characters
TIMEOUT = 1

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def capture_garbled_characters():
    """Capture and analyze the garbled characters"""
    log("🔍 Garbled Characters Capture")
    log("=" * 50)
    
    log("📋 INSTRUCTIONS:")
    log("1. Keep the camera powered on")
    log("2. The script will monitor for weird characters")
    log("3. When you see them, they will be captured and analyzed")
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
        
        log("🚀 Monitoring started...")
        log("💡 Try power cycling the camera or pressing reset button")
        
        character_count = 0
        
        while True:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                if data:
                    character_count += len(data)
                    log(f"📥 Captured {len(data)} characters (total: {character_count})")
                    
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
        return False
    except Exception as e:
        log(f"❌ Monitoring error: {e}")
        return False
    finally:
        if 'ser' in locals():
            ser.close()
            log("🔌 USB connection closed")

def try_alternative_baud_rates():
    """Try alternative baud rates when 115200 shows garbled characters"""
    log("\n🔍 Trying Alternative Baud Rates")
    log("=" * 50)
    
    # Common baud rates for embedded systems
    baud_rates = [57600, 38400, 19200, 9600, 230400, 460800, 921600]
    
    for baud_rate in baud_rates:
        log(f"🔄 Testing baud rate: {baud_rate}")
        
        try:
            ser = serial.Serial(
                port=SERIAL_PORT,
                baudrate=baud_rate,
                timeout=TIMEOUT
            )
            
            # Monitor for 5 seconds
            start_time = time.time()
            data_received = False
            
            while time.time() - start_time < 5:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    if data:
                        data_received = True
                        log(f"📥 Data at {baud_rate}: {repr(data)}")
                        
                        # Try to decode
                        try:
                            decoded = data.decode('utf-8', errors='replace')
                            log(f"📥 Decoded: {repr(decoded)}")
                            
                            # Check for readable text
                            if any(c.isalpha() or c.isdigit() for c in decoded):
                                log(f"✅ Readable text at {baud_rate} bps!")
                                return baud_rate
                        except:
                            pass
                time.sleep(0.1)
            
            ser.close()
            
            if data_received:
                log(f"✅ Data received at {baud_rate} bps")
            else:
                log(f"📥 No data at {baud_rate} bps")
                
        except Exception as e:
            log(f"❌ Failed at {baud_rate} bps: {e}")
    
    return None

def main():
    """Main function"""
    print("🔧 DCS-8000LH Garbled Characters Capture")
    print("=" * 60)
    print("Capturing and analyzing the weird characters you're seeing")
    print()
    
    # Step 1: Try alternative baud rates first
    correct_baud = try_alternative_baud_rates()
    
    if correct_baud:
        log(f"✅ Found working baud rate: {correct_baud} bps")
        log("💡 Use this baud rate for communication")
    else:
        log("⚠️ No alternative baud rate found")
        log("💡 Proceeding with 115200 bps monitoring")
    
    # Step 2: Continuous monitoring at 115200
    log(f"\n{'='*60}")
    success = capture_garbled_characters()
    
    if success:
        log("✅ Bootloader communication established!")
        log("💡 You can now proceed with firmware flashing")
    else:
        log("❌ Bootloader communication not established")
        log("💡 Try power cycling the camera or pressing reset button")

if __name__ == "__main__":
    main()







