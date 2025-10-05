#!/usr/bin/env python3

"""
USB Camera IP Discovery Script for DCS-8000LH
Uses USB communication to get camera's network information
"""

import serial
import time
import sys
import os
import re

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
BAUD_RATE = 115200
TIMEOUT = 5

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

def get_network_info(ser):
    """Get camera network information"""
    print("\n🌐 Getting Network Information...")
    print("=" * 50)
    
    # Try different commands to get network info
    network_commands = [
        "ifconfig",
        "ip addr",
        "ip route",
        "netstat -rn",
        "route -n",
        "cat /proc/net/route",
        "cat /proc/net/arp",
        "arp -a",
        "ping -c 1 192.168.1.1",
        "ping -c 1 8.8.8.8",
    ]
    
    network_info = {}
    
    for cmd in network_commands:
        response = send_command(ser, cmd, 3)
        
        # Extract IP addresses from response
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ips = re.findall(ip_pattern, response)
        
        if ips:
            print(f"✅ Found IPs: {ips}")
            network_info[cmd] = ips
    
    return network_info

def get_uboot_network_info(ser):
    """Get network info from U-Boot environment"""
    print("\n🔧 Getting U-Boot Network Info...")
    print("=" * 50)
    
    uboot_commands = [
        "printenv ipaddr",
        "printenv serverip", 
        "printenv gatewayip",
        "printenv netmask",
        "printenv ethaddr",
        "printenv",
    ]
    
    uboot_info = {}
    
    for cmd in uboot_commands:
        response = send_command(ser, cmd, 2)
        
        # Extract network info from U-Boot environment
        if "=" in response:
            key, value = response.split("=", 1)
            uboot_info[key.strip()] = value.strip()
            print(f"✅ {key.strip()}: {value.strip()}")
    
    return uboot_info

def try_boot_and_get_info(ser):
    """Try to boot camera and get network info"""
    print("\n🐧 Attempting to Boot and Get Info...")
    print("=" * 50)
    
    boot_commands = [
        "boot",
        "run bootcmd",
        "go 0x80000000",
    ]
    
    for cmd in boot_commands:
        response = send_command(ser, cmd, 5)
        
        # Look for network information in boot output
        if any(keyword in response.lower() for keyword in ['ip', 'network', 'interface', 'eth0', 'wlan0']):
            print(f"✅ Boot command '{cmd}' found network info!")
            return response
    
    return ""

def main():
    """Main function"""
    print("🔌 DCS-8000LH USB Camera IP Discovery")
    print("=" * 60)
    print(f"Serial Port: {SERIAL_PORT}")
    print("")
    
    # Connect to camera
    ser = connect_to_camera()
    if not ser:
        print("❌ Cannot connect to camera via USB")
        return
    
    try:
        # Get U-Boot network info
        uboot_info = get_uboot_network_info(ser)
        
        # Try to get network info from running system
        network_info = get_network_info(ser)
        
        # Try to boot and get info
        boot_info = try_boot_and_get_info(ser)
        
        # Compile results
        print("\n📋 Camera Network Information:")
        print("=" * 50)
        
        if uboot_info:
            print("🔧 U-Boot Environment:")
            for key, value in uboot_info.items():
                print(f"  {key}: {value}")
        
        if network_info:
            print("\n🌐 Network Commands:")
            for cmd, ips in network_info.items():
                print(f"  {cmd}: {ips}")
        
        if boot_info:
            print("\n🐧 Boot Information:")
            print(f"  {boot_info}")
        
        # Try to determine camera IP
        camera_ip = None
        
        # Check U-Boot environment for IP
        if 'ipaddr' in uboot_info:
            camera_ip = uboot_info['ipaddr']
            print(f"\n✅ Camera IP from U-Boot: {camera_ip}")
        
        # Check network commands for IPs
        all_ips = []
        for cmd, ips in network_info.items():
            all_ips.extend(ips)
        
        if all_ips:
            print(f"\n✅ Found IPs: {set(all_ips)}")
            # Use the first non-gateway IP
            for ip in set(all_ips):
                if not ip.endswith('.1') and not ip.startswith('127.'):
                    camera_ip = ip
                    break
        
        if camera_ip:
            print(f"\n🎯 Camera IP: {camera_ip}")
            
            # Save camera IP to file
            with open('camera_ip.txt', 'w') as f:
                f.write(f"CAMERA_IP={camera_ip}\n")
            
            print(f"💾 Saved camera IP to camera_ip.txt")
            
            # Test camera access
            print(f"\n🧪 Testing camera access at {camera_ip}...")
            import subprocess
            result = subprocess.run(['curl', '-I', f'http://{camera_ip}'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ Camera accessible at http://{camera_ip}")
            else:
                print(f"❌ Camera not accessible at http://{camera_ip}")
        else:
            print("\n❌ Could not determine camera IP")
            print("💡 Camera may not be connected to network or needs different approach")
        
    except KeyboardInterrupt:
        print("\n⚠️ Discovery interrupted by user")
    except Exception as e:
        print(f"❌ Error during discovery: {e}")
    finally:
        if ser:
            ser.close()
            print("🔌 USB connection closed")

if __name__ == "__main__":
    main()
