#!/usr/bin/env python3

"""
Continuous Monitor for DCS-8000LH
Continuously monitors for communication and tries to decode it
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

def continuous_monitor():
    """Continuously monitor for communication"""
    log("🔍 Continuous Communication Monitor")
    log("=" * 50)
    
    log("📋 INSTRUCTIONS:")
    log("1. Keep the camera powered on")
    log("2. The script will monitor for any communication")
    log("3. When you see weird characters, they will be analyzed")
    log("4. Press Ctrl+C to stop monitoring")
    log("")
    
    log("⏳ Starting continuous monitoring...")
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
        
        while True:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                if data:
                    log(f"📥 Raw data received: {len(data)} bytes")
                    log(f"📥 Raw hex: {data.hex()}")
                    log(f"📥 Raw bytes: {[hex(b) for b in data]}")
                    
                    # Try different decoding methods
                    try:
                        decoded_utf8 = data.decode('utf-8', errors='replace')
                        log(f"📥 UTF-8: {repr(decoded_utf8)}")
                    except:
                        pass
                    
                    try:
                        decoded_ascii = data.decode('ascii', errors='replace')
                        log(f"📥 ASCII: {repr(decoded_ascii)}")
                    except:
                        pass
                    
                    try:
                        decoded_latin1 = data.decode('latin-1', errors='replace')
                        log(f"📥 Latin-1: {repr(decoded_latin1)}")
                    except:
                        pass
                    
                    # Check for bootloader indicators
                    if any(keyword in data.decode('utf-8', errors='ignore').lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version']):
                        log("✅ BOOTLOADER DETECTED!")
                        log("💡 Camera is in bootloader mode")
                        return True
                    
                    log("")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        log("\n⚠️ Monitoring stopped by user")
        return False
    except Exception as e:
        log(f"❌ Monitoring error: {e}")
        return False
    finally:
        if 'ser' in locals():
            ser.close()
            log("🔌 USB connection closed")

def try_different_baud_rates():
    """Try different baud rates to find the correct one"""
    log("\n🔍 Trying Different Baud Rates")
    log("=" * 50)
    
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
                time.sleep(0.1)
            
            ser.close()
            
            if data_received:
                log(f"✅ Data received at {baud_rate}")
                return baud_rate
            else:
                log(f"📥 No data at {baud_rate}")
                
        except Exception as e:
            log(f"❌ Failed at {baud_rate}: {e}")
    
    return None

def main():
    """Main function"""
    print("🔧 DCS-8000LH Continuous Monitor")
    print("=" * 60)
    print("Continuously monitors for communication and tries to decode it")
    print()
    
    # Step 1: Try different baud rates first
    correct_baud = try_different_baud_rates()
    
    if correct_baud:
        log(f"✅ Found working baud rate: {correct_baud}")
        log("💡 Use this baud rate for communication")
    else:
        log("⚠️ No working baud rate found")
        log("💡 Proceeding with continuous monitoring")
    
    # Step 2: Continuous monitoring
    log("\n" + "="*60)
    success = continuous_monitor()
    
    if success:
        log("✅ Bootloader communication established!")
        log("💡 You can now proceed with firmware flashing")
    else:
        log("❌ Bootloader communication not established")
        log("💡 Try power cycling the camera or pressing reset button")

if __name__ == "__main__":
    main()







