#!/usr/bin/env python3

"""
Interactive USB Camera Configuration Script for DCS-8000LH
Attempts to get camera into interactive mode for proper command execution
"""

import serial
import time
import sys
import os

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

def send_command(ser, command, wait_time=2):
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

def try_boot_interrupt(ser):
    """Try to interrupt the boot process to get to U-Boot or shell"""
    print("\n🔄 Attempting Boot Interrupt...")
    print("=" * 50)
    
    # Try different interrupt sequences
    interrupts = [
        "\x03",  # Ctrl+C
        "\x04",  # Ctrl+D
        "\x1A",  # Ctrl+Z
        "\x7F",  # Backspace
        "\r",    # Enter
        "\n",    # Newline
        " ",     # Space
    ]
    
    for interrupt in interrupts:
        print(f"Trying interrupt: {repr(interrupt)}")
        ser.write(interrupt.encode())
        time.sleep(1)
        
        # Check for response
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"Response: {response}")
            if any(keyword in response.lower() for keyword in ['uboot', 'boot', 'shell', 'prompt', '>', '#', '$']):
                print("✅ Found interactive prompt!")
                return True
    
    return False

def try_uboot_commands(ser):
    """Try U-Boot specific commands"""
    print("\n🔧 Trying U-Boot Commands...")
    print("=" * 50)
    
    uboot_commands = [
        "help",
        "printenv",
        "setenv",
        "boot",
        "reset",
        "run",
        "md",
        "mw",
        "tftp",
        "ping",
        "dhcp",
    ]
    
    for cmd in uboot_commands:
        response = send_command(ser, cmd, 2)
        if any(keyword in response.lower() for keyword in ['help', 'usage', 'command', 'available']):
            print(f"✅ U-Boot command '{cmd}' responded!")
            return True
    
    return False

def try_shell_commands(ser):
    """Try shell commands"""
    print("\n🐚 Trying Shell Commands...")
    print("=" * 50)
    
    shell_commands = [
        "sh",
        "bash",
        "ash",
        "busybox",
        "ls",
        "pwd",
        "whoami",
        "id",
        "ps",
        "netstat",
    ]
    
    for cmd in shell_commands:
        response = send_command(ser, cmd, 2)
        if any(keyword in response.lower() for keyword in ['directory', 'file', 'process', 'user', 'root']):
            print(f"✅ Shell command '{cmd}' responded!")
            return True
    
    return False

def try_special_sequences(ser):
    """Try special key sequences to get interactive mode"""
    print("\n⌨️ Trying Special Key Sequences...")
    print("=" * 50)
    
    sequences = [
        # Multiple enters
        "\r\n\r\n\r\n",
        # Multiple spaces
        "   ",
        # Tab completion
        "\t",
        # Escape sequences
        "\x1B",
        "\x1B[A",  # Up arrow
        "\x1B[B",  # Down arrow
        "\x1B[C",  # Right arrow
        "\x1B[D",  # Left arrow
        # Function keys
        "\x1BOP",  # F1
        "\x1BOQ",  # F2
        "\x1BOR",  # F3
        "\x1BOS",  # F4
    ]
    
    for seq in sequences:
        print(f"Trying sequence: {repr(seq)}")
        ser.write(seq.encode())
        time.sleep(1)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"Response: {response}")
            if any(keyword in response.lower() for keyword in ['prompt', 'shell', 'command', '>', '#', '$']):
                print("✅ Found interactive prompt!")
                return True
    
    return False

def try_direct_commands(ser):
    """Try direct command execution"""
    print("\n⚡ Trying Direct Commands...")
    print("=" * 50)
    
    # Try to execute commands directly
    direct_commands = [
        "echo 'Hello from camera'",
        "date",
        "uptime",
        "free",
        "df -h",
        "mount",
        "ls /",
        "cat /proc/version",
        "cat /proc/cpuinfo",
        "ifconfig",
    ]
    
    for cmd in direct_commands:
        response = send_command(ser, cmd, 3)
        if any(keyword in response.lower() for keyword in ['hello', 'date', 'uptime', 'memory', 'filesystem', 'mounted', 'linux', 'cpu', 'interface']):
            print(f"✅ Command '{cmd}' executed successfully!")
            print(f"Response: {response}")
            return True
    
    return False

def main():
    """Main function"""
    print("🔌 DCS-8000LH Interactive USB Configuration")
    print("=" * 60)
    print(f"Serial Port: {SERIAL_PORT}")
    print("")
    
    # Connect to camera
    ser = connect_to_camera()
    if not ser:
        print("❌ Cannot connect to camera via USB")
        return
    
    try:
        # Try different approaches to get interactive mode
        print("🔍 Attempting to get camera into interactive mode...")
        
        # Method 1: Boot interrupt
        if try_boot_interrupt(ser):
            print("✅ Boot interrupt successful!")
            return
        
        # Method 2: U-Boot commands
        if try_uboot_commands(ser):
            print("✅ U-Boot commands working!")
            return
        
        # Method 3: Shell commands
        if try_shell_commands(ser):
            print("✅ Shell commands working!")
            return
        
        # Method 4: Special sequences
        if try_special_sequences(ser):
            print("✅ Special sequences successful!")
            return
        
        # Method 5: Direct commands
        if try_direct_commands(ser):
            print("✅ Direct commands working!")
            return
        
        print("❌ Could not get camera into interactive mode")
        print("💡 The camera may be in a non-interactive state or require different approach")
        
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
