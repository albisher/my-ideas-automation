#!/usr/bin/env python3

"""
USB Firmware Flashing Script for DCS-8000LH
Attempts to flash custom firmware via USB communication
"""

import serial
import time
import sys
import os
import subprocess

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
BAUD_RATE = 115200
TIMEOUT = 5
FIRMWARE_FILE = "/Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts/fw.tar"

def connect_to_camera():
    """Connect to camera via USB serial"""
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=TIMEOUT,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        print(f"✅ Connected to camera via {SERIAL_PORT}")
        return ser
    except Exception as e:
        print(f"❌ Failed to connect to camera: {e}")
        return None

def send_command(ser, command, wait_time=3):
    """Send command to camera and wait for response"""
    try:
        print(f"📤 Sending: {command}")
        ser.write(f"{command}\r\n".encode())
        time.sleep(wait_time)
        
        # Read response
        response = ""
        while ser.in_waiting > 0:
            response += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            time.sleep(0.1)
        
        if response.strip():
            print(f"📥 Response: {response.strip()}")
        return response
    except Exception as e:
        print(f"❌ Error sending command: {e}")
        return ""

def try_uboot_flash(ser):
    """Try to flash firmware via U-Boot commands"""
    print("\n🔧 Attempting U-Boot Firmware Flash...")
    print("=" * 50)
    
    # Try to get into U-Boot mode
    print("🔄 Trying to get into U-Boot mode...")
    
    # Send boot interrupt sequences
    interrupt_sequences = [
        '\x03',  # Ctrl+C
        '\x04',  # Ctrl+D
        '\x1a',  # Ctrl+Z
        '\r',    # Enter
        '\n',    # Newline
    ]
    
    for char in interrupt_sequences:
        ser.write(char.encode())
        time.sleep(0.5)
        response = ser.read_all().decode(errors='ignore').strip()
        if response:
            print(f"Response to {repr(char)}: {response}")
            if any(keyword in response.lower() for keyword in ['uboot', 'boot', 'prompt']):
                print("✅ U-Boot mode detected!")
                break
    
    # Try U-Boot commands
    uboot_commands = [
        "help",
        "printenv",
        "version",
        "reset",
        "boot",
        "run bootcmd",
        "go 0x80000000",
    ]
    
    for cmd in uboot_commands:
        response = send_command(ser, cmd, 2)
        if response and response != cmd:
            print(f"✅ U-Boot command '{cmd}' responded: {response}")
            break
    
    # Try to set up network for TFTP
    print("\n🌐 Setting up network for firmware transfer...")
    network_commands = [
        "setenv ipaddr 192.168.1.100",
        "setenv serverip 192.168.1.1", 
        "setenv gatewayip 192.168.1.1",
        "setenv netmask 255.255.255.0",
        "setenv ethaddr B0:C5:54:51:EB:76",
        "saveenv",
    ]
    
    for cmd in network_commands:
        send_command(ser, cmd, 1)
    
    # Try TFTP commands
    print("\n📡 Attempting TFTP firmware transfer...")
    tftp_commands = [
        "tftp 0x80000000 fw.tar",
        "tftp 0x80000000 firmware.bin",
        "tftp 0x80000000 update.bin",
        "tftp 0x80000000 defogger.bin",
    ]
    
    for cmd in tftp_commands:
        response = send_command(ser, cmd, 5)
        if response and "bytes transferred" in response.lower():
            print(f"✅ TFTP transfer successful: {response}")
            return True
    
    return False

def try_direct_flash(ser):
    """Try direct firmware flashing methods"""
    print("\n⚡ Attempting Direct Firmware Flash...")
    print("=" * 50)
    
    # Try different flash commands
    flash_commands = [
        "flash write 0x80000000 0x9f000000 0x100000",
        "cp.b 0x80000000 0x9f000000 0x100000",
        "erase 0x9f000000 +0x100000",
        "protect off 0x9f000000 +0x100000",
        "erase 0x9f000000 +0x100000",
        "cp.b 0x80000000 0x9f000000 0x100000",
        "protect on 0x9f000000 +0x100000",
        "bootm 0x80000000",
        "go 0x80000000",
    ]
    
    for cmd in flash_commands:
        response = send_command(ser, cmd, 3)
        if response and response != cmd:
            print(f"✅ Flash command '{cmd}' responded: {response}")
            return True
    
    return False

def try_firmware_upload(ser):
    """Try to upload firmware via serial"""
    print("\n📤 Attempting Serial Firmware Upload...")
    print("=" * 50)
    
    if not os.path.exists(FIRMWARE_FILE):
        print(f"❌ Firmware file not found: {FIRMWARE_FILE}")
        return False
    
    print(f"📁 Firmware file: {FIRMWARE_FILE}")
    print(f"📊 File size: {os.path.getsize(FIRMWARE_FILE)} bytes")
    
    # Try different upload methods
    upload_commands = [
        "loadb 0x80000000",
        "loads 0x80000000", 
        "loadx 0x80000000",
        "loady 0x80000000",
        "loadz 0x80000000",
    ]
    
    for cmd in upload_commands:
        print(f"🔄 Trying upload command: {cmd}")
        response = send_command(ser, cmd, 2)
        
        if response and "ready" in response.lower():
            print(f"✅ Upload command ready: {response}")
            
            # Try to send firmware data
            try:
                with open(FIRMWARE_FILE, 'rb') as f:
                    data = f.read()
                    print(f"📤 Sending {len(data)} bytes of firmware...")
                    ser.write(data)
                    time.sleep(5)
                    
                    response = ser.read_all().decode(errors='ignore').strip()
                    if response:
                        print(f"📥 Upload response: {response}")
                        return True
            except Exception as e:
                print(f"❌ Error uploading firmware: {e}")
    
    return False

def try_recovery_mode(ser):
    """Try to get camera into recovery mode"""
    print("\n🔄 Attempting Recovery Mode...")
    print("=" * 50)
    
    # Try different recovery sequences
    recovery_sequences = [
        # Multiple resets
        ['reset', 'reset', 'reset'],
        # Boot with different parameters
        ['setenv bootargs recovery', 'boot'],
        ['setenv bootargs single', 'boot'],
        ['setenv bootargs init=/bin/sh', 'boot'],
        # Memory operations
        ['md 0x80000000 10'],
        ['mw 0x80000000 0x12345678'],
        # Direct execution
        ['go 0x80000000'],
        ['exec 0x80000000'],
    ]
    
    for sequence in recovery_sequences:
        print(f"🔄 Trying recovery sequence: {sequence}")
        for cmd in sequence:
            response = send_command(ser, cmd, 2)
            if response and response != cmd:
                print(f"✅ Recovery command '{cmd}' responded: {response}")
                return True
    
    return False

def main():
    """Main function"""
    print("🔧 DCS-8000LH USB Firmware Flash")
    print("=" * 60)
    print(f"Serial Port: {SERIAL_PORT}")
    print(f"Firmware: {FIRMWARE_FILE}")
    print("")
    
    # Check if firmware exists
    if not os.path.exists(FIRMWARE_FILE):
        print(f"❌ Firmware file not found: {FIRMWARE_FILE}")
        print("💡 Please build the firmware first using: ./run-defogger-commands.sh build")
        return
    
    # Connect to camera
    ser = connect_to_camera()
    if not ser:
        return
    
    try:
        # Clear any pending input/output
        ser.flushInput()
        ser.flushOutput()
        time.sleep(1)
        
        # Try different flashing methods
        methods = [
            ("U-Boot Flash", try_uboot_flash),
            ("Direct Flash", try_direct_flash),
            ("Firmware Upload", try_firmware_upload),
            ("Recovery Mode", try_recovery_mode),
        ]
        
        for method_name, method_func in methods:
            print(f"\n🔧 Trying {method_name}...")
            if method_func(ser):
                print(f"✅ {method_name} successful!")
                break
            else:
                print(f"❌ {method_name} failed")
        
        print("\n🎯 Firmware flash attempt completed!")
        print("💡 Check if camera is now accessible on network")
        
    except KeyboardInterrupt:
        print("\n⚠️ Firmware flash interrupted by user")
    except Exception as e:
        print(f"❌ Error during firmware flash: {e}")
    finally:
        if ser:
            ser.close()
            print("🔌 USB connection closed")

if __name__ == "__main__":
    main()
