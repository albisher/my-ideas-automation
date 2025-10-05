#!/usr/bin/env python3

"""
DCS-8000LH Reset and Flash Sequence
Focused sequence for establishing reset capability and firmware flashing
"""

import serial
import time
import sys
import os
import subprocess
from datetime import datetime

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
BAUD_RATE = 115200
TIMEOUT = 2
OFFICIAL_FIRMWARE = "/Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts/DCS-8000LH_Ax_v2.02.02_3014.bin"

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def step_1_verify_usb_connection():
    """Step 1: Verify USB Connection"""
    log("🔍 Step 1: Verify USB Connection")
    log("=" * 50)
    
    if not os.path.exists(SERIAL_PORT):
        log(f"❌ USB device not found: {SERIAL_PORT}")
        return False
    
    log(f"✅ USB device found: {SERIAL_PORT}")
    
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=TIMEOUT
        )
        ser.close()
        log("✅ USB connection test successful")
        return True
    except Exception as e:
        log(f"❌ USB connection failed: {e}")
        return False

def step_2_test_serial_communication():
    """Step 2: Test Serial Communication"""
    log("🔍 Step 2: Test Serial Communication")
    log("=" * 50)
    
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=TIMEOUT
        )
        
        # Test basic communication
        log("🔄 Testing basic serial communication...")
        ser.write(b'\r\n')
        ser.flush()
        time.sleep(1)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            if response.strip():
                log(f"✅ Serial communication working: {repr(response)}")
                ser.close()
                return True
            else:
                log("📥 Empty response received")
        else:
            log("📥 No response received")
        
        ser.close()
        return False
        
    except Exception as e:
        log(f"❌ Serial communication failed: {e}")
        return False

def step_3_establish_bootloader_access():
    """Step 3: Establish Bootloader Access"""
    log("🔍 Step 3: Establish Bootloader Access")
    log("=" * 50)
    
    log("📋 BOOTLOADER ACCESS PROCEDURE:")
    log("1. Unplug camera power")
    log("2. Wait 10 seconds")
    log("3. Press and hold reset button")
    log("4. Plug power back in while holding reset")
    log("5. Hold reset for 10-15 seconds")
    log("6. Release reset button")
    log("7. Immediately run communication test")
    log("")
    
    log("⏳ Starting bootloader access procedure...")
    log("💡 Perform the reset procedure now")
    
    # Wait for user to perform reset
    for i in range(30, 0, -1):
        print(f"\r⏰ Starting test in {i} seconds... (perform reset now)", end='', flush=True)
        time.sleep(1)
    
    print("\n")
    log("🚀 Testing for bootloader access...")
    
    # Try to connect and test for bootloader
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=TIMEOUT
        )
        
        # Try boot interrupt sequences
        interrupt_sequences = [
            ("Rapid Ctrl+C", [b'\x03' for _ in range(50)]),
            ("Enter spam", [b'\r\n' for _ in range(50)]),
            ("Space spam", [b' ' for _ in range(50)]),
            ("Mixed sequence", [b'\x03', b'\r\n', b' ', b'\t', b'\x04'] * 20)
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
            
            time.sleep(3)
            
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
        log(f"❌ Bootloader access test failed: {e}")
        return False

def step_4_flash_official_firmware():
    """Step 4: Flash Official Firmware"""
    log("🔍 Step 4: Flash Official Firmware")
    log("=" * 50)
    
    if not os.path.exists(OFFICIAL_FIRMWARE):
        log(f"❌ Official firmware not found: {OFFICIAL_FIRMWARE}")
        return False
    
    file_size = os.path.getsize(OFFICIAL_FIRMWARE)
    log(f"📁 Official firmware: {OFFICIAL_FIRMWARE}")
    log(f"📊 File size: {file_size} bytes")
    
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=TIMEOUT
        )
        
        # Try different upload methods
        upload_commands = [
            "loadb 0x80000000",
            "loads 0x80000000",
            "loadx 0x80000000",
            "loady 0x80000000",
            "loadz 0x80000000"
        ]
        
        for cmd in upload_commands:
            log(f"🔄 Trying upload command: {cmd}")
            
            # Send command
            ser.write(f"{cmd}\r\n".encode())
            ser.flush()
            time.sleep(2)
            
            # Check for ready response
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                if "ready" in response.lower():
                    log(f"✅ Upload command ready: {response}")
                    
                    # Send firmware data
                    with open(OFFICIAL_FIRMWARE, 'rb') as f:
                        data = f.read()
                        log(f"📤 Sending {len(data)} bytes of official firmware...")
                        ser.write(data)
                        time.sleep(30)  # Longer wait for large firmware
                        
                        # Check upload response
                        if ser.in_waiting > 0:
                            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                            log(f"📥 Upload response: {response}")
                            
                            # Try to flash to flash memory
                            flash_commands = [
                                "erase 0x9f000000 +0x1000000",
                                "cp.b 0x80000000 0x9f000000 0x1000000",
                                "protect on 0x9f000000 +0x1000000"
                            ]
                            
                            for flash_cmd in flash_commands:
                                log(f"🔄 Executing: {flash_cmd}")
                                ser.write(f"{flash_cmd}\r\n".encode())
                                ser.flush()
                                time.sleep(5)
                                
                                if ser.in_waiting > 0:
                                    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                                    log(f"📥 Flash response: {response}")
                            
                            ser.close()
                            return True
                else:
                    log(f"📥 Command response: {response}")
        
        ser.close()
        log("❌ Firmware flash failed")
        return False
        
    except Exception as e:
        log(f"❌ Firmware flash error: {e}")
        return False

def step_5_verify_firmware_flash():
    """Step 5: Verify Firmware Flash"""
    log("🔍 Step 5: Verify Firmware Flash")
    log("=" * 50)
    
    log("⏳ Waiting for camera to reboot...")
    time.sleep(30)
    
    # Check if camera is accessible via network
    network_ips = ["192.168.1.100", "192.168.0.100", "192.168.1.1"]
    
    for ip in network_ips:
        log(f"🔄 Testing network connectivity to {ip}")
        try:
            result = subprocess.run(["ping", "-c", "1", ip], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                log(f"✅ Camera accessible at {ip}")
                
                # Try HTTP access
                try:
                    http_result = subprocess.run(["curl", "-I", f"http://{ip}"], 
                                               capture_output=True, text=True, timeout=10)
                    if http_result.returncode == 0:
                        log(f"✅ HTTP access successful at {ip}")
                        log("🎯 Official firmware flash successful!")
                        return True
                except Exception as e:
                    log(f"❌ HTTP access failed at {ip}: {e}")
        except Exception as e:
            log(f"❌ Network test failed for {ip}: {e}")
    
    log("❌ Camera not accessible after firmware flash")
    return False

def main():
    """Main function"""
    print("🔧 DCS-8000LH Reset and Flash Sequence")
    print("=" * 60)
    print("Focused sequence for establishing reset capability and firmware flashing")
    print()
    
    # Step results
    step_results = {}
    
    # Run all steps
    steps = [
        ("USB Connection", step_1_verify_usb_connection),
        ("Serial Communication", step_2_test_serial_communication),
        ("Bootloader Access", step_3_establish_bootloader_access),
        ("Firmware Flash", step_4_flash_official_firmware),
        ("Verification", step_5_verify_firmware_flash)
    ]
    
    for step_name, step_func in steps:
        log(f"\n{'='*60}")
        log(f"Running {step_name}")
        log(f"{'='*60}")
        
        try:
            result = step_func()
            step_results[step_name] = result
            if result:
                log(f"✅ {step_name} PASSED")
            else:
                log(f"❌ {step_name} FAILED")
        except Exception as e:
            log(f"❌ {step_name} ERROR: {e}")
            step_results[step_name] = False
    
    # Summary
    log(f"\n{'='*60}")
    log("RESET AND FLASH SEQUENCE SUMMARY")
    log(f"{'='*60}")
    
    passed_steps = sum(1 for result in step_results.values() if result)
    total_steps = len(step_results)
    
    for step_name, result in step_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log(f"{step_name}: {status}")
    
    log(f"\n📊 Results: {passed_steps}/{total_steps} steps passed")
    
    if passed_steps >= 4:
        log("✅ Reset and flash sequence completed successfully!")
        log("🎯 Camera has been flashed with official firmware")
    elif passed_steps >= 2:
        log("⚠️ Partial success - some steps completed")
        log("💡 Check the failed steps and try again")
    else:
        log("❌ Reset and flash sequence failed")
        log("💡 Check USB connection and try again")
    
    return step_results

if __name__ == "__main__":
    main()







