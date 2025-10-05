#!/usr/bin/env python3

"""
Analyze Garbled Communication for DCS-8000LH
Decode and analyze the weird characters we're receiving
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

def analyze_garbled_communication():
    """Analyze the garbled communication we're receiving"""
    log("🔍 Analyzing Garbled Communication")
    log("=" * 50)
    
    log("✅ GOOD NEWS: We're getting communication!")
    log("📥 The weird characters mean the TX/RX flip worked")
    log("🔧 Now we need to decode the proper communication")
    log("")
    
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=TIMEOUT,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        
        log("🔄 Monitoring communication for 10 seconds...")
        start_time = time.time()
        raw_data = b""
        
        while time.time() - start_time < 10:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                raw_data += data
                print(f"📥 Raw: {data}", end='', flush=True)
            time.sleep(0.1)
        
        ser.close()
        
        if raw_data:
            log(f"\n📊 Total bytes received: {len(raw_data)}")
            log(f"📥 Raw data: {raw_data}")
            
            # Try different decoding methods
            log("\n🔧 Trying different decoding methods...")
            
            # Method 1: UTF-8 with error handling
            try:
                decoded_utf8 = raw_data.decode('utf-8', errors='replace')
                log(f"📥 UTF-8 decoded: {repr(decoded_utf8)}")
            except Exception as e:
                log(f"❌ UTF-8 decode failed: {e}")
            
            # Method 2: ASCII with error handling
            try:
                decoded_ascii = raw_data.decode('ascii', errors='replace')
                log(f"📥 ASCII decoded: {repr(decoded_ascii)}")
            except Exception as e:
                log(f"❌ ASCII decode failed: {e}")
            
            # Method 3: Latin-1
            try:
                decoded_latin1 = raw_data.decode('latin-1', errors='replace')
                log(f"📥 Latin-1 decoded: {repr(decoded_latin1)}")
            except Exception as e:
                log(f"❌ Latin-1 decode failed: {e}")
            
            # Method 4: Raw hex
            log(f"📥 Raw hex: {raw_data.hex()}")
            
            # Method 5: Individual bytes
            log(f"📥 Individual bytes: {[hex(b) for b in raw_data]}")
            
            return True, raw_data
        else:
            log("❌ No data received")
            return False, None
            
    except Exception as e:
        log(f"❌ Communication analysis failed: {e}")
        return False, None

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
            
            # Monitor for 3 seconds
            start_time = time.time()
            data_received = False
            
            while time.time() - start_time < 3:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    if data:
                        data_received = True
                        print(f"📥 {data}", end='', flush=True)
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

def try_boot_interrupt_with_correct_baud():
    """Try boot interrupt with the correct baud rate"""
    log("\n🔍 Trying Boot Interrupt with Correct Baud Rate")
    log("=" * 50)
    
    # First find the correct baud rate
    correct_baud = try_different_baud_rates()
    
    if not correct_baud:
        log("❌ No working baud rate found")
        return False
    
    log(f"✅ Using baud rate: {correct_baud}")
    
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=correct_baud,
            timeout=TIMEOUT
        )
        
        # Try boot interrupt sequences
        interrupt_sequences = [
            ("Rapid Ctrl+C", [b'\x03' for _ in range(30)]),
            ("Enter spam", [b'\r\n' for _ in range(30)]),
            ("Space spam", [b' ' for _ in range(30)]),
            ("Mixed sequence", [b'\x03', b'\r\n', b' ', b'\t', b'\x04'] * 10)
        ]
        
        for seq_name, sequence in interrupt_sequences:
            log(f"🔄 Trying {seq_name}")
            
            # Clear buffers
            ser.flushInput()
            ser.flushOutput()
            time.sleep(0.5)
            
            # Send interrupt sequence
            for char in sequence:
                ser.write(char)
                time.sleep(0.1)
            
            time.sleep(2)
            
            # Check for response
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                if any(keyword in response.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version']):
                    log(f"✅ Bootloader access established with {seq_name}")
                    log(f"📥 Response: {response}")
                    ser.close()
                    return True
                else:
                    log(f"📥 Response: {response}")
        
        ser.close()
        log("❌ Bootloader access not established")
        return False
        
    except Exception as e:
        log(f"❌ Boot interrupt test failed: {e}")
        return False

def main():
    """Main function"""
    print("🔧 DCS-8000LH Garbled Communication Analysis")
    print("=" * 60)
    print("Analyzing the weird characters we're receiving")
    print()
    
    # Step 1: Analyze the garbled communication
    success, raw_data = analyze_garbled_communication()
    
    if success:
        log("✅ Communication established!")
        log("💡 The TX/RX flip worked - we're getting data")
        
        # Step 2: Try different baud rates
        correct_baud = try_different_baud_rates()
        
        if correct_baud:
            log(f"✅ Found working baud rate: {correct_baud}")
            
            # Step 3: Try boot interrupt
            if try_boot_interrupt_with_correct_baud():
                log("✅ Bootloader access established!")
                log("💡 You can now proceed with firmware flashing")
            else:
                log("⚠️ Bootloader access not established")
                log("💡 Camera may be in normal operation mode")
        else:
            log("❌ No working baud rate found")
            log("💡 Try different baud rates or check camera status")
    else:
        log("❌ No communication established")
        log("💡 Check wiring and try again")

if __name__ == "__main__":
    main()







