#!/usr/bin/env python3

"""
Test Correct Baud Rate for DCS-8000LH
Test both 115200 and 57600 baud rates to find the correct one
"""

import serial
import time
import sys
import os
from datetime import datetime

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
TIMEOUT = 2

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_baud_rate(baud_rate):
    """Test specific baud rate"""
    log(f"🔄 Testing baud rate: {baud_rate}")
    
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=baud_rate,
            timeout=TIMEOUT,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        
        log(f"📡 Connected at {baud_rate} bps")
        log("⏳ Monitoring for 10 seconds...")
        
        start_time = time.time()
        data_received = False
        raw_data = b""
        
        while time.time() - start_time < 10:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                if data:
                    data_received = True
                    raw_data += data
                    print(f"📥 {data}", end='', flush=True)
            time.sleep(0.1)
        
        ser.close()
        
        if data_received:
            log(f"\n✅ Data received at {baud_rate} bps")
            log(f"📊 Total bytes: {len(raw_data)}")
            
            # Try to decode the data
            try:
                decoded = raw_data.decode('utf-8', errors='replace')
                log(f"📥 Decoded: {repr(decoded)}")
                
                # Check for bootloader indicators
                if any(keyword in decoded.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version', 'boot']):
                    log("🎯 BOOTLOADER DETECTED!")
                    return True, decoded
                else:
                    log("📥 Normal boot messages")
                    return True, decoded
                    
            except Exception as e:
                log(f"❌ Decode error: {e}")
                return True, raw_data
        else:
            log(f"📥 No data at {baud_rate} bps")
            return False, None
            
    except Exception as e:
        log(f"❌ Failed at {baud_rate} bps: {e}")
        return False, None

def main():
    """Main function"""
    print("🔧 DCS-8000LH Correct Baud Rate Test")
    print("=" * 60)
    print("Testing both 115200 and 57600 baud rates")
    print()
    
    # Test both baud rates
    baud_rates = [115200, 57600]
    results = {}
    
    for baud_rate in baud_rates:
        log(f"\n{'='*50}")
        success, data = test_baud_rate(baud_rate)
        results[baud_rate] = (success, data)
        
        if success:
            log(f"✅ {baud_rate} bps: Communication successful")
        else:
            log(f"❌ {baud_rate} bps: No communication")
    
    # Summary
    log(f"\n{'='*60}")
    log("📊 SUMMARY")
    log("=" * 60)
    
    working_baud = None
    for baud_rate, (success, data) in results.items():
        if success:
            log(f"✅ {baud_rate} bps: WORKING")
            if not working_baud:
                working_baud = baud_rate
        else:
            log(f"❌ {baud_rate} bps: Not working")
    
    if working_baud:
        log(f"\n🎯 RECOMMENDED BAUD RATE: {working_baud} bps")
        log("💡 Use this baud rate for firmware flashing")
        
        # Check if bootloader is accessible
        success, data = results[working_baud]
        if data and any(keyword in str(data).lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version', 'boot']):
            log("🚀 BOOTLOADER ACCESS: Available")
            log("💡 You can now proceed with firmware flashing")
        else:
            log("⚠️ BOOTLOADER ACCESS: Not detected")
            log("💡 Camera may be in normal operation mode")
            log("💡 Try power cycling or pressing reset button")
    else:
        log("\n❌ NO WORKING BAUD RATE FOUND")
        log("💡 Check wiring and camera power status")

if __name__ == "__main__":
    main()







