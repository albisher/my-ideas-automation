#!/usr/bin/env python3

"""
U-Boot USB Camera Configuration Script for DCS-8000LH
Uses U-Boot commands to configure the camera for streaming
"""

import serial
import time
import sys
import os

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
BAUD_RATE = 115200
TIMEOUT = 5

# Camera configuration
CAMERA_MAC = "B0:C5:54:51:EB:76"
CAMERA_PIN = "052446"
WIFI_SSID = "SA"
WIFI_PASSWORD = "62Dad64Mom"

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

def send_uboot_command(ser, command, wait_time=3):
    """Send U-Boot command to camera and wait for response"""
    try:
        print(f"📤 U-Boot: {command}")
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
        print(f"❌ Error sending U-Boot command: {e}")
        return ""

def get_uboot_help(ser):
    """Get U-Boot help to see available commands"""
    print("\n🔍 Getting U-Boot Help...")
    print("=" * 50)
    
    help_response = send_uboot_command(ser, "help", 5)
    if "help" in help_response.lower():
        print("✅ U-Boot help received")
        return True
    return False

def check_uboot_environment(ser):
    """Check U-Boot environment variables"""
    print("\n🌍 Checking U-Boot Environment...")
    print("=" * 50)
    
    env_response = send_uboot_command(ser, "printenv", 5)
    if "printenv" in env_response.lower():
        print("✅ U-Boot environment accessible")
        return True
    return False

def set_network_environment(ser):
    """Set network environment variables"""
    print("\n🌐 Setting Network Environment...")
    print("=" * 50)
    
    network_commands = [
        f"setenv ipaddr 192.168.1.100",
        f"setenv serverip 192.168.1.1",
        f"setenv gatewayip 192.168.1.1",
        f"setenv netmask 255.255.255.0",
        f"setenv ethaddr {CAMERA_MAC}",
        f"setenv wifi_ssid '{WIFI_SSID}'",
        f"setenv wifi_password '{WIFI_PASSWORD}'",
        "saveenv",
    ]
    
    for cmd in network_commands:
        send_uboot_command(ser, cmd, 2)
        time.sleep(1)
    
    print("✅ Network environment set")

def try_boot_linux(ser):
    """Try to boot into Linux"""
    print("\n🐧 Attempting to Boot Linux...")
    print("=" * 50)
    
    boot_commands = [
        "boot",
        "run bootcmd",
        "run bootargs",
        "bootm",
        "go 0x80000000",
    ]
    
    for cmd in boot_commands:
        response = send_uboot_command(ser, cmd, 5)
        if any(keyword in response.lower() for keyword in ['linux', 'kernel', 'booting', 'starting']):
            print(f"✅ Boot command '{cmd}' successful!")
            return True
    
    return False

def try_tftp_boot(ser):
    """Try TFTP boot to load custom firmware"""
    print("\n📡 Attempting TFTP Boot...")
    print("=" * 50)
    
    tftp_commands = [
        "tftp 0x80000000 fw.tar",
        "tftp 0x80000000 defogger.bin",
        "tftp 0x80000000 firmware.bin",
        "tftp 0x80000000 update.bin",
    ]
    
    for cmd in tftp_commands:
        response = send_uboot_command(ser, cmd, 10)
        if any(keyword in response.lower() for keyword in ['tftp', 'loading', 'bytes', 'done', 'success']):
            print(f"✅ TFTP command '{cmd}' successful!")
            return True
    
    return False

def try_memory_operations(ser):
    """Try memory operations to modify camera behavior"""
    print("\n💾 Attempting Memory Operations...")
    print("=" * 50)
    
    memory_commands = [
        "md 0x80000000 10",  # Display memory
        "mw 0x80000000 0x12345678",  # Write to memory
        "md 0x80000000 1",  # Read back
        "md 0x10000000 10",  # Check different memory region
        "md 0x20000000 10",  # Check another region
    ]
    
    for cmd in memory_commands:
        response = send_uboot_command(ser, cmd, 3)
        if any(keyword in response.lower() for keyword in ['memory', 'address', 'data', '0x']):
            print(f"✅ Memory command '{cmd}' successful!")
            return True
    
    return False

def try_reset_and_boot(ser):
    """Try to reset and boot with custom parameters"""
    print("\n🔄 Attempting Reset and Boot...")
    print("=" * 50)
    
    reset_commands = [
        "reset",
        "run bootcmd",
        "bootm 0x80000000",
        "go 0x80000000",
    ]
    
    for cmd in reset_commands:
        response = send_uboot_command(ser, cmd, 5)
        if any(keyword in response.lower() for keyword in ['reset', 'booting', 'starting', 'linux']):
            print(f"✅ Reset command '{cmd}' successful!")
            return True
    
    return False

def try_direct_execution(ser):
    """Try to execute commands directly"""
    print("\n⚡ Attempting Direct Execution...")
    print("=" * 50)
    
    direct_commands = [
        "run",
        "exec",
        "sh",
        "bash",
        "ash",
        "busybox",
    ]
    
    for cmd in direct_commands:
        response = send_uboot_command(ser, cmd, 3)
        if any(keyword in response.lower() for keyword in ['shell', 'command', 'executing', 'running']):
            print(f"✅ Direct execution '{cmd}' successful!")
            return True
    
    return False

def main():
    """Main function"""
    print("🔌 DCS-8000LH U-Boot USB Configuration")
    print("=" * 60)
    print(f"Camera MAC: {CAMERA_MAC}")
    print(f"Camera PIN: {CAMERA_PIN}")
    print(f"WiFi SSID: {WIFI_SSID}")
    print(f"Serial Port: {SERIAL_PORT}")
    print("")
    
    # Connect to camera
    ser = connect_to_camera()
    if not ser:
        print("❌ Cannot connect to camera via USB")
        return
    
    try:
        # Get U-Boot help
        if get_uboot_help(ser):
            print("✅ U-Boot help received")
        
        # Check environment
        if check_uboot_environment(ser):
            print("✅ U-Boot environment accessible")
        
        # Set network environment
        set_network_environment(ser)
        
        # Try different boot methods
        if try_boot_linux(ser):
            print("✅ Linux boot successful!")
            return
        
        if try_tftp_boot(ser):
            print("✅ TFTP boot successful!")
            return
        
        if try_memory_operations(ser):
            print("✅ Memory operations successful!")
            return
        
        if try_reset_and_boot(ser):
            print("✅ Reset and boot successful!")
            return
        
        if try_direct_execution(ser):
            print("✅ Direct execution successful!")
            return
        
        print("❌ Could not configure camera through U-Boot")
        print("💡 Camera may need different approach or firmware")
        
    except KeyboardInterrupt:
        print("\n⚠️ Configuration interrupted by user")
    except Exception as e:
        print(f"❌ Error during configuration: {e}")
    finally:
        if ser:
            ser.close()
            print("🔌 USB connection closed")

if __name__ == "__main__":
    main()
