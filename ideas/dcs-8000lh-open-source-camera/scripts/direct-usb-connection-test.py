#!/usr/bin/env python3

"""
Direct USB Connection Test for DCS-8000LH
Test direct USB connection and communication
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

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_usb_connection():
    """Test direct USB connection"""
    log("🔍 Direct USB Connection Test")
    log("=" * 50)
    
    try:
        # Test connection
        log(f"🔄 Connecting to {SERIAL_PORT} at {BAUD_RATE} bps...")
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=TIMEOUT,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        
        log("✅ USB connection established")
        log(f"📊 Port: {ser.port}")
        log(f"📊 Baud rate: {ser.baudrate}")
        log(f"📊 Timeout: {ser.timeout}")
        log(f"📊 Parity: {ser.parity}")
        log(f"📊 Stop bits: {ser.stopbits}")
        log(f"📊 Data bits: {ser.bytesize}")
        
        return ser
        
    except Exception as e:
        log(f"❌ USB connection failed: {e}")
        return None

def test_communication(ser):
    """Test communication with camera"""
    log("\n🔍 Communication Test")
    log("=" * 50)
    
    if not ser:
        log("❌ No serial connection available")
        return False
    
    try:
        # Clear buffers
        ser.flushInput()
        ser.flushOutput()
        log("🧹 Buffers cleared")
        
        # Test 1: Check for incoming data
        log("🔄 Testing for incoming data...")
        time.sleep(1)
        
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            log(f"📥 Incoming data: {data}")
            log(f"📥 Hex: {data.hex()}")
            log(f"📥 Bytes: {[hex(b) for b in data]}")
        else:
            log("📥 No incoming data")
        
        # Test 2: Send test command
        log("🔄 Sending test command...")
        test_command = b"\r\n"
        ser.write(test_command)
        log(f"📤 Sent: {test_command}")
        
        time.sleep(1)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            log(f"📥 Response: {response}")
            log(f"📥 Hex: {response.hex()}")
        else:
            log("📥 No response")
        
        # Test 3: Try boot interrupt
        log("🔄 Trying boot interrupt...")
        interrupt_sequence = [b'\x03', b'\r\n', b' ', b'\t'] * 5
        
        for char in interrupt_sequence:
            ser.write(char)
            time.sleep(0.1)
        
        log("📤 Sent interrupt sequence")
        time.sleep(2)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            log(f"📥 Response: {response}")
            log(f"📥 Hex: {response.hex()}")
            
            # Try to decode
            try:
                decoded = response.decode('utf-8', errors='replace')
                log(f"📥 Decoded: {repr(decoded)}")
                
                # Check for bootloader
                if any(keyword in decoded.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version', 'boot', 'alpha168']):
                    log("🎯 BOOTLOADER DETECTED!")
                    return True
            except:
                pass
        else:
            log("📥 No response to interrupt")
        
        return False
        
    except Exception as e:
        log(f"❌ Communication test failed: {e}")
        return False

def monitor_continuous(ser):
    """Continuous monitoring for data"""
    log("\n🔍 Continuous Monitoring")
    log("=" * 50)
    
    if not ser:
        log("❌ No serial connection available")
        return False
    
    log("⏳ Monitoring for 30 seconds...")
    log("💡 Try power cycling the camera or pressing reset button")
    
    start_time = time.time()
    data_count = 0
    
    try:
        while time.time() - start_time < 30:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                if data:
                    data_count += 1
                    log(f"📥 Data {data_count}: {data}")
                    log(f"📥 Hex: {data.hex()}")
                    log(f"📥 Bytes: {[hex(b) for b in data]}")
                    
                    # Try to decode
                    try:
                        decoded = data.decode('utf-8', errors='replace')
                        log(f"📥 Decoded: {repr(decoded)}")
                        
                        # Check for bootloader
                        if any(keyword in decoded.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version', 'boot', 'alpha168']):
                            log("🎯 BOOTLOADER DETECTED!")
                            return True
                    except:
                        pass
                    
                    print("")
            
            time.sleep(0.1)
        
        log(f"📊 Total data packets received: {data_count}")
        return False
        
    except Exception as e:
        log(f"❌ Monitoring failed: {e}")
        return False

def main():
    """Main function"""
    print("🔧 DCS-8000LH Direct USB Connection Test")
    print("=" * 60)
    print("Testing direct USB connection and communication")
    print()
    
    # Step 1: Test USB connection
    ser = test_usb_connection()
    
    if not ser:
        log("❌ Cannot establish USB connection")
        log("💡 Check wiring and camera power status")
        return
    
    try:
        # Step 2: Test communication
        comm_success = test_communication(ser)
        
        if comm_success:
            log("✅ Communication successful!")
            log("💡 Bootloader access established")
        else:
            log("⚠️ Basic communication test completed")
            
            # Step 3: Continuous monitoring
            monitor_success = monitor_continuous(ser)
            
            if monitor_success:
                log("✅ Bootloader detected during monitoring!")
                log("💡 You can now proceed with firmware flashing")
            else:
                log("❌ No bootloader detected")
                log("💡 Try power cycling the camera or pressing reset button")
    
    finally:
        if ser:
            ser.close()
            log("🔌 USB connection closed")

if __name__ == "__main__":
    main()







