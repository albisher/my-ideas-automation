#!/usr/bin/env python3

"""
DCS-8000LH Wiring Verification
Checks for indicators that wiring might be incorrect
"""

import serial
import time
import sys
import os
from datetime import datetime

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
BAUD_RATES = [115200, 57600, 38400, 19200, 9600, 230400]
TIMEOUT = 2

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_wiring_indicators():
    """Check for indicators that wiring might be wrong"""
    log("🔍 Checking for wiring problem indicators...")
    log("=" * 60)
    
    indicators = {
        "no_serial_response": False,
        "no_boot_messages": False,
        "no_power_indicators": False,
        "inconsistent_baud_rates": False,
        "connection_drops": False,
        "garbled_data": False
    }
    
    # Test 1: No serial response at any baud rate
    log("🔄 Test 1: Serial response at different baud rates")
    no_response_count = 0
    
    for baud_rate in BAUD_RATES:
        try:
            ser = serial.Serial(
                port=SERIAL_PORT,
                baudrate=baud_rate,
                timeout=TIMEOUT
            )
            
            # Send test command
            ser.write(b'\r\n')
            ser.flush()
            time.sleep(1)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                if response.strip():
                    log(f"✅ Response at {baud_rate}: {repr(response)}")
                else:
                    log(f"📥 Empty response at {baud_rate}")
                    no_response_count += 1
            else:
                log(f"📥 No response at {baud_rate}")
                no_response_count += 1
            
            ser.close()
            
        except Exception as e:
            log(f"❌ Failed at {baud_rate}: {e}")
            no_response_count += 1
    
    if no_response_count == len(BAUD_RATES):
        indicators["no_serial_response"] = True
        log("⚠️ INDICATOR: No serial response at any baud rate")
    
    # Test 2: Check for garbled data
    log("\n🔄 Test 2: Checking for garbled data")
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=115200,
            timeout=TIMEOUT
        )
        
        # Send various test sequences
        test_sequences = [
            b'\r\n',
            b'\x03',
            b' ',
            b'\t',
            b'help\r\n',
            b'version\r\n'
        ]
        
        garbled_found = False
        for seq in test_sequences:
            ser.write(seq)
            ser.flush()
            time.sleep(0.5)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                # Check for garbled characters
                if any(ord(c) > 127 for c in response if c.isprintable()):
                    log(f"⚠️ Garbled data detected: {repr(response)}")
                    garbled_found = True
        
        if garbled_found:
            indicators["garbled_data"] = True
            log("⚠️ INDICATOR: Garbled data received")
        
        ser.close()
        
    except Exception as e:
        log(f"❌ Garbled data test failed: {e}")
    
    # Test 3: Connection stability
    log("\n🔄 Test 3: Connection stability")
    connection_drops = 0
    
    for i in range(5):
        try:
            ser = serial.Serial(
                port=SERIAL_PORT,
                baudrate=115200,
                timeout=TIMEOUT
            )
            time.sleep(0.5)
            ser.close()
            log(f"✅ Connection {i+1} stable")
        except Exception as e:
            log(f"❌ Connection {i+1} failed: {e}")
            connection_drops += 1
    
    if connection_drops > 2:
        indicators["connection_drops"] = True
        log("⚠️ INDICATOR: Frequent connection drops")
    
    return indicators

def check_power_indicators():
    """Check for power-related indicators"""
    log("\n🔍 Checking power indicators...")
    log("=" * 60)
    
    power_indicators = {
        "no_power_led": False,
        "no_boot_sequence": False,
        "inconsistent_power": False
    }
    
    log("📋 POWER INDICATOR CHECKLIST:")
    log("1. Is the camera power LED on?")
    log("2. Does the camera show any boot sequence?")
    log("3. Does the camera create a WiFi hotspot?")
    log("4. Does the camera respond to network pings?")
    log("")
    
    # Check for network indicators
    log("🔄 Checking for network power indicators...")
    network_ips = ["192.168.1.100", "192.168.0.100", "192.168.1.1"]
    
    network_accessible = False
    for ip in network_ips:
        try:
            import subprocess
            result = subprocess.run(["ping", "-c", "1", ip], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                log(f"✅ Network accessible at {ip}")
                network_accessible = True
                break
        except Exception:
            pass
    
    if not network_accessible:
        power_indicators["no_boot_sequence"] = True
        log("⚠️ INDICATOR: No network accessibility")
    
    return power_indicators

def check_wiring_solutions():
    """Provide wiring solutions based on indicators"""
    log("\n🔧 Wiring Solutions Based on Indicators")
    log("=" * 60)
    
    indicators = check_wiring_indicators()
    power_indicators = check_power_indicators()
    
    all_indicators = {**indicators, **power_indicators}
    
    log("📋 WIRING PROBLEM INDICATORS FOUND:")
    for indicator, found in all_indicators.items():
        if found:
            log(f"⚠️ {indicator.replace('_', ' ').title()}")
    
    if not any(all_indicators.values()):
        log("✅ No wiring problem indicators found")
        log("💡 Wiring appears to be correct")
        return
    
    log("\n🔧 RECOMMENDED WIRING SOLUTIONS:")
    
    if all_indicators.get("no_serial_response"):
        log("1. Check USB-to-Serial adapter connections:")
        log("   - TX (Transmit) should connect to RX (Receive) on camera")
        log("   - RX (Receive) should connect to TX (Transmit) on camera")
        log("   - GND (Ground) should connect to GND on camera")
        log("   - Do NOT connect VCC/3.3V unless specifically required")
    
    if all_indicators.get("garbled_data"):
        log("2. Check for wiring issues:")
        log("   - Loose connections")
        log("   - Wrong baud rate")
        log("   - Interference from other devices")
        log("   - Poor quality USB cable")
    
    if all_indicators.get("connection_drops"):
        log("3. Check connection stability:")
        log("   - Secure all connections")
        log("   - Check for loose wires")
        log("   - Try different USB port")
        log("   - Check USB cable quality")
    
    if all_indicators.get("no_boot_sequence"):
        log("4. Check power connections:")
        log("   - Ensure camera is properly powered")
        log("   - Check power adapter")
        log("   - Verify camera is actually booting")
    
    log("\n📋 CORRECT WIRING DIAGRAM:")
    log("USB-to-Serial Adapter -> Camera")
    log("TX (Pin 2) -> RX (Camera)")
    log("RX (Pin 3) -> TX (Camera)")
    log("GND (Pin 5) -> GND (Camera)")
    log("VCC (Pin 1) -> NOT CONNECTED (unless required)")
    
    log("\n⚠️ COMMON WIRING MISTAKES:")
    log("1. TX connected to TX (should be TX to RX)")
    log("2. RX connected to RX (should be RX to TX)")
    log("3. VCC connected when not needed")
    log("4. Loose connections")
    log("5. Wrong pin assignments")

def main():
    """Main function"""
    print("🔧 DCS-8000LH Wiring Verification")
    print("=" * 60)
    print("Checking for indicators that wiring might be incorrect")
    print()
    
    # Check wiring indicators
    check_wiring_solutions()
    
    log("\n💡 NEXT STEPS:")
    log("1. Verify wiring connections")
    log("2. Check power indicators")
    log("3. Test with different USB cable")
    log("4. Try different USB port")
    log("5. Check camera power status")

if __name__ == "__main__":
    main()







