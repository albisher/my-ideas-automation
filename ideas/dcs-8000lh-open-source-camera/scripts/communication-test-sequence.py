#!/usr/bin/env python3

"""
DCS-8000LH Communication Test Sequence
Comprehensive testing to establish proper communication and reset capability
"""

import serial
import time
import sys
import os
import subprocess
from datetime import datetime

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
BAUD_RATES = [115200, 57600, 38400, 19200, 9600, 230400]
TIMEOUT = 2

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_1_usb_device_detection():
    """Test 1: USB Device Detection"""
    log("🔍 Test 1: USB Device Detection")
    log("=" * 50)
    
    if os.path.exists(SERIAL_PORT):
        log(f"✅ USB device found: {SERIAL_PORT}")
        
        # Check device permissions
        try:
            stat = os.stat(SERIAL_PORT)
            log(f"📊 Device permissions: {oct(stat.st_mode)[-3:]}")
            return True
        except Exception as e:
            log(f"❌ Device permission check failed: {e}")
            return False
    else:
        log(f"❌ USB device not found: {SERIAL_PORT}")
        return False

def test_2_serial_connection():
    """Test 2: Serial Connection"""
    log("🔍 Test 2: Serial Connection")
    log("=" * 50)
    
    working_connections = []
    
    for baud_rate in BAUD_RATES:
        try:
            log(f"🔄 Testing baud rate: {baud_rate}")
            ser = serial.Serial(
                port=SERIAL_PORT,
                baudrate=baud_rate,
                timeout=TIMEOUT,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            
            # Test basic communication
            ser.write(b'\r\n')
            ser.flush()
            time.sleep(1)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                if response.strip():
                    log(f"✅ Response at {baud_rate}: {repr(response)}")
                    working_connections.append((ser, baud_rate, response))
                else:
                    log(f"📥 Empty response at {baud_rate}")
            else:
                log(f"📥 No response at {baud_rate}")
            
            ser.close()
            
        except Exception as e:
            log(f"❌ Failed at {baud_rate}: {e}")
    
    if working_connections:
        log(f"✅ Found {len(working_connections)} working connections")
        return working_connections
    else:
        log("❌ No working serial connections found")
        return []

def test_3_boot_interrupt_sequences():
    """Test 3: Boot Interrupt Sequences"""
    log("🔍 Test 3: Boot Interrupt Sequences")
    log("=" * 50)
    
    working_connections = test_2_serial_connection()
    if not working_connections:
        log("❌ No working connections for boot interrupt test")
        return False
    
    for ser, baud_rate, initial_response in working_connections:
        log(f"\n🔄 Testing boot interrupt at {baud_rate}")
        
        try:
            # Clear buffers
            ser.flushInput()
            ser.flushOutput()
            time.sleep(0.5)
            
            # Try different interrupt sequences
            interrupt_sequences = [
                ("Rapid Ctrl+C", [b'\x03' for _ in range(30)]),
                ("Enter spam", [b'\r\n' for _ in range(30)]),
                ("Space spam", [b' ' for _ in range(30)]),
                ("Mixed sequence", [b'\x03', b'\r\n', b' ', b'\t', b'\x04'] * 10)
            ]
            
            for seq_name, sequence in interrupt_sequences:
                log(f"🔄 Trying {seq_name}")
                
                for char in sequence:
                    ser.write(char)
                    time.sleep(0.1)
                
                time.sleep(2)
                
                # Check for response
                if ser.in_waiting > 0:
                    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    if any(keyword in response.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version']):
                        log(f"✅ Boot interrupt successful with {seq_name}")
                        log(f"📥 Response: {response}")
                        ser.close()
                        return True
                    else:
                        log(f"📥 Response: {response}")
            
            ser.close()
            
        except Exception as e:
            log(f"❌ Boot interrupt test failed at {baud_rate}: {e}")
    
    return False

def test_4_power_cycle_detection():
    """Test 4: Power Cycle Detection"""
    log("🔍 Test 4: Power Cycle Detection")
    log("=" * 50)
    
    log("📋 INSTRUCTIONS:")
    log("1. Unplug camera power")
    log("2. Wait 10 seconds")
    log("3. Press and hold reset button")
    log("4. Plug power back in while holding reset")
    log("5. Hold reset for 5-10 seconds")
    log("6. Release reset button")
    log("")
    
    log("⏳ Starting power cycle monitoring...")
    log("💡 Perform the power cycle now")
    
    # Wait for user to power cycle
    for i in range(30, 0, -1):
        print(f"\r⏰ Starting monitoring in {i} seconds... (power cycle now)", end='', flush=True)
        time.sleep(1)
    
    print("\n")
    log("🚀 Starting power cycle monitoring...")
    
    # Monitor for boot messages
    for baud_rate in [115200, 57600]:
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
            log(f"❌ Power cycle monitoring failed at {baud_rate}: {e}")
    
    return False, None, None

def test_5_network_communication():
    """Test 5: Network Communication"""
    log("🔍 Test 5: Network Communication")
    log("=" * 50)
    
    network_ips = ["192.168.1.100", "192.168.0.100", "192.168.1.1", "192.168.0.1"]
    
    for ip in network_ips:
        log(f"🔄 Testing network connectivity to {ip}")
        try:
            result = subprocess.run(["ping", "-c", "1", ip], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                log(f"✅ Camera reachable at {ip}")
                
                # Try HTTP access
                try:
                    http_result = subprocess.run(["curl", "-I", f"http://{ip}"], 
                                               capture_output=True, text=True, timeout=10)
                    if http_result.returncode == 0:
                        log(f"✅ HTTP access successful at {ip}")
                        return True, ip
                except Exception as e:
                    log(f"❌ HTTP access failed at {ip}: {e}")
            else:
                log(f"❌ No response from {ip}")
        except Exception as e:
            log(f"❌ Network test failed for {ip}: {e}")
    
    return False, None

def test_6_bluetooth_communication():
    """Test 6: Bluetooth Communication"""
    log("🔍 Test 6: Bluetooth Communication")
    log("=" * 50)
    
    try:
        # Check if bluepy is available
        import bluepy
        log("✅ Bluepy library available")
        
        # Try to scan for Bluetooth devices
        from bluepy.btle import Scanner
        scanner = Scanner()
        devices = scanner.scan(10.0)
        
        log(f"📡 Found {len(devices)} Bluetooth devices")
        
        for device in devices:
            if device.addr:
                log(f"📱 Device: {device.addr} - {device.addrType}")
                if "B0:C5:54:51:EB:76" in device.addr:
                    log("✅ Camera Bluetooth device found!")
                    return True
        
        log("❌ Camera Bluetooth device not found")
        return False
        
    except ImportError:
        log("❌ Bluepy library not available")
        return False
    except Exception as e:
        log(f"❌ Bluetooth communication test failed: {e}")
        return False

def test_7_reset_capability():
    """Test 7: Reset Capability"""
    log("🔍 Test 7: Reset Capability")
    log("=" * 50)
    
    log("📋 RESET CAPABILITY TEST:")
    log("1. Camera should be powered on")
    log("2. Press and hold reset button for 10 seconds")
    log("3. Release reset button")
    log("4. Wait 30 seconds")
    log("5. Check if camera behavior changed")
    log("")
    
    log("⏳ Waiting for reset test...")
    log("💡 Press and hold reset button for 10 seconds now")
    
    # Wait for user to perform reset
    time.sleep(60)  # Wait 1 minute for reset test
    
    # Check if camera behavior changed
    log("🔍 Checking for reset effects...")
    
    # Test network connectivity
    network_result, ip = test_5_network_communication()
    if network_result:
        log(f"✅ Camera accessible after reset at {ip}")
        return True
    else:
        log("❌ No network access after reset")
        return False

def main():
    """Main function"""
    print("🔧 DCS-8000LH Communication Test Sequence")
    print("=" * 60)
    print("Comprehensive testing to establish communication and reset capability")
    print()
    
    # Test results
    test_results = {}
    
    # Run all tests
    tests = [
        ("USB Device Detection", test_1_usb_device_detection),
        ("Serial Connection", test_2_serial_connection),
        ("Boot Interrupt Sequences", test_3_boot_interrupt_sequences),
        ("Power Cycle Detection", test_4_power_cycle_detection),
        ("Network Communication", test_5_network_communication),
        ("Bluetooth Communication", test_6_bluetooth_communication),
        ("Reset Capability", test_7_reset_capability)
    ]
    
    for test_name, test_func in tests:
        log(f"\n{'='*60}")
        log(f"Running {test_name}")
        log(f"{'='*60}")
        
        try:
            result = test_func()
            test_results[test_name] = result
            if result:
                log(f"✅ {test_name} PASSED")
            else:
                log(f"❌ {test_name} FAILED")
        except Exception as e:
            log(f"❌ {test_name} ERROR: {e}")
            test_results[test_name] = False
    
    # Summary
    log(f"\n{'='*60}")
    log("TEST SEQUENCE SUMMARY")
    log(f"{'='*60}")
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log(f"{test_name}: {status}")
    
    log(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests >= 3:
        log("✅ Communication established - camera is accessible")
        log("💡 You can now proceed with firmware flashing")
    else:
        log("❌ Communication not established")
        log("💡 Check USB connection and try again")
    
    return test_results

if __name__ == "__main__":
    main()







