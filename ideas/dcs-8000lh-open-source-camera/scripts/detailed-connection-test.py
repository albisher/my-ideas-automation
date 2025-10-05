#!/usr/bin/env python3

"""
Detailed Connection Test for DCS-8000LH
Comprehensive test to diagnose connection issues
"""

import serial
import time
import sys
import os
import subprocess
from datetime import datetime

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
BAUD_RATES = [115200, 57600, 38400, 19200, 9600, 230400, 460800, 921600]
TIMEOUT = 3

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_camera_power_status():
    """Test if camera is actually powered on"""
    log("🔍 Testing Camera Power Status")
    log("=" * 50)
    
    log("📋 POWER STATUS CHECKLIST:")
    log("1. Is the camera power LED on?")
    log("2. Does the camera show any boot sequence?")
    log("3. Does the camera create a WiFi hotspot?")
    log("4. Does the camera respond to network pings?")
    log("")
    
    # Check for network indicators
    log("🔄 Checking for network power indicators...")
    network_ips = ["192.168.1.100", "192.168.0.100", "192.168.1.1", "192.168.0.1"]
    
    network_accessible = False
    for ip in network_ips:
        try:
            result = subprocess.run(["ping", "-c", "1", ip], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                log(f"✅ Network accessible at {ip}")
                network_accessible = True
                break
        except Exception:
            pass
    
    if not network_accessible:
        log("❌ No network accessibility - camera may not be powered on")
        log("💡 Check camera power adapter and power LED")
        return False
    else:
        log("✅ Camera appears to be powered on")
        return True

def test_serial_communication_detailed():
    """Detailed serial communication test"""
    log("🔍 Detailed Serial Communication Test")
    log("=" * 50)
    
    for baud_rate in BAUD_RATES:
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
            
            # Test multiple communication methods
            test_sequences = [
                ("Enter", b'\r\n'),
                ("Ctrl+C", b'\x03'),
                ("Space", b' '),
                ("Tab", b'\t'),
                ("Help", b'help\r\n'),
                ("Version", b'version\r\n'),
                ("Info", b'info\r\n'),
                ("Status", b'status\r\n')
            ]
            
            for seq_name, sequence in test_sequences:
                log(f"  🔄 Testing {seq_name}")
                ser.write(sequence)
                ser.flush()
                time.sleep(1)
                
                if ser.in_waiting > 0:
                    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    if response.strip():
                        log(f"  ✅ Response to {seq_name}: {repr(response)}")
                        ser.close()
                        return True, baud_rate, response
                    else:
                        log(f"  📥 Empty response to {seq_name}")
                else:
                    log(f"  📥 No response to {seq_name}")
            
            ser.close()
            
        except Exception as e:
            log(f"❌ Failed at {baud_rate}: {e}")
    
    return False, None, None

def test_continuous_monitoring():
    """Test continuous monitoring for boot messages"""
    log("🔍 Continuous Monitoring Test")
    log("=" * 50)
    
    log("📋 INSTRUCTIONS:")
    log("1. Power cycle the camera (unplug and plug back in)")
    log("2. The script will monitor for boot messages")
    log("3. Look for any output during boot process")
    log("")
    
    log("⏳ Starting continuous monitoring...")
    log("💡 Power cycle the camera now")
    
    # Wait for user to power cycle
    for i in range(30, 0, -1):
        print(f"\r⏰ Starting monitoring in {i} seconds... (power cycle now)", end='', flush=True)
        time.sleep(1)
    
    print("\n")
    log("🚀 Starting continuous monitoring...")
    
    # Monitor for boot messages
    for baud_rate in [115200, 57600, 38400]:
        try:
            log(f"👁️ Monitoring at {baud_rate} for boot messages...")
            ser = serial.Serial(
                port=SERIAL_PORT,
                baudrate=baud_rate,
                timeout=1
            )
            
            start_time = time.time()
            boot_messages = ""
            
            while time.time() - start_time < 60:  # Monitor for 60 seconds
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    text = data.decode('utf-8', errors='ignore')
                    boot_messages += text
                    print(f"📥 {text}", end='', flush=True)
                    
                    # Check for boot indicators
                    if any(keyword in text.lower() for keyword in ['boot', 'uboot', 'linux', 'kernel', 'init', 'rlxboot']):
                        log(f"✅ Boot message detected at {baud_rate}")
                        ser.close()
                        return True, baud_rate, boot_messages
                
                time.sleep(0.1)
            
            ser.close()
            
        except Exception as e:
            log(f"❌ Continuous monitoring failed at {baud_rate}: {e}")
    
    return False, None, None

def test_wiring_alternatives():
    """Test alternative wiring configurations"""
    log("🔍 Testing Alternative Wiring Configurations")
    log("=" * 50)
    
    log("📋 ALTERNATIVE WIRING TO TRY:")
    log("1. TX -> TX, RX -> RX (direct connection)")
    log("2. TX -> RX, RX -> TX (crossed connection)")
    log("3. Only GND connected (minimal connection)")
    log("4. Try different USB-to-Serial adapter")
    log("5. Try different USB cable")
    log("")
    
    log("💡 CURRENT WIRING STATUS:")
    log("You mentioned you flipped TX/RX connections")
    log("Please verify your current wiring:")
    log("- TX (USB) -> RX (Camera)")
    log("- RX (USB) -> TX (Camera)")
    log("- GND (USB) -> GND (Camera)")
    log("- VCC (USB) -> NOT CONNECTED")
    log("")
    
    log("🔄 Testing current wiring configuration...")
    
    # Test with current configuration
    success, baud_rate, response = test_serial_communication_detailed()
    
    if success:
        log(f"✅ Current wiring configuration works at {baud_rate}")
        return True
    else:
        log("❌ Current wiring configuration not working")
        log("💡 Try the alternative configurations listed above")
        return False

def main():
    """Main function"""
    print("🔧 DCS-8000LH Detailed Connection Test")
    print("=" * 60)
    print("Comprehensive test to diagnose connection issues")
    print()
    
    # Test 1: Camera power status
    power_status = test_camera_power_status()
    
    # Test 2: Detailed serial communication
    log("\n" + "="*60)
    serial_success, baud_rate, response = test_serial_communication_detailed()
    
    if serial_success:
        log(f"✅ Serial communication working at {baud_rate}")
        log(f"📥 Response: {response}")
    else:
        log("❌ Serial communication not working")
    
    # Test 3: Continuous monitoring
    log("\n" + "="*60)
    monitor_success, monitor_baud, boot_messages = test_continuous_monitoring()
    
    if monitor_success:
        log(f"✅ Boot messages detected at {monitor_baud}")
        log(f"📥 Boot messages: {boot_messages}")
    else:
        log("❌ No boot messages detected")
    
    # Test 4: Wiring alternatives
    log("\n" + "="*60)
    wiring_success = test_wiring_alternatives()
    
    # Summary
    log("\n" + "="*60)
    log("DETAILED CONNECTION TEST SUMMARY")
    log("="*60)
    
    log(f"Power Status: {'✅ Working' if power_status else '❌ Not Working'}")
    log(f"Serial Communication: {'✅ Working' if serial_success else '❌ Not Working'}")
    log(f"Boot Messages: {'✅ Detected' if monitor_success else '❌ Not Detected'}")
    log(f"Wiring Configuration: {'✅ Working' if wiring_success else '❌ Not Working'}")
    
    if serial_success or monitor_success:
        log("\n✅ Communication established!")
        log("💡 You can now proceed with firmware flashing")
    else:
        log("\n❌ Communication not established")
        log("💡 Check wiring, power, and try alternative configurations")

if __name__ == "__main__":
    main()







