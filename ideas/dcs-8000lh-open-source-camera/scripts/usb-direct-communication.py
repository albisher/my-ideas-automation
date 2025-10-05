#!/usr/bin/env python3

"""
Direct USB Communication Script for DCS-8000LH
Tries various methods to get camera into interactive mode
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
    """Try to interrupt the boot process"""
    print("\n🔄 Attempting Boot Interrupt...")
    print("=" * 50)
    
    # Try different interrupt sequences
    interrupt_sequences = [
        ['\x03', '\x04', '\x1a'],  # Ctrl+C, Ctrl+D, Ctrl+Z
        ['\r', '\n', ' '],         # Enter, Newline, Space
        ['\x7f', '\x08'],          # Delete, Backspace
        ['\x1b', '\x1c'],          # Escape sequences
    ]
    
    for sequence in interrupt_sequences:
        print(f"Trying interrupt sequence: {[repr(c) for c in sequence]}")
        for char in sequence:
            ser.write(char.encode())
            time.sleep(0.1)
            response = ser.read_all().decode(errors='ignore').strip()
            if response:
                print(f"Response: {response}")
                if any(keyword in response.lower() for keyword in ['uboot', 'boot', 'prompt', '#', '$']):
                    print("✅ Boot interrupt successful!")
                    return True
        time.sleep(1)
    
    return False

def try_different_baud_rates():
    """Try different baud rates"""
    print("\n🔧 Trying Different Baud Rates...")
    print("=" * 50)
    
    baud_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800]
    
    for baud in baud_rates:
        try:
            print(f"Trying baud rate: {baud}")
            ser = serial.Serial(SERIAL_PORT, baud, timeout=1)
            time.sleep(0.5)
            
            # Send test command
            ser.write(b"help\r\n")
            time.sleep(1)
            response = ser.read_all().decode(errors='ignore').strip()
            
            if response and response != "help":
                print(f"✅ Response at {baud}: {response}")
                ser.close()
                return baud
            else:
                print(f"❌ No response at {baud}")
            
            ser.close()
        except Exception as e:
            print(f"❌ Error at {baud}: {e}")
    
    return None

def try_direct_commands(ser):
    """Try direct commands to get interactive mode"""
    print("\n🎯 Trying Direct Commands...")
    print("=" * 50)
    
    # Try different command approaches
    commands = [
        "help",
        "version", 
        "info",
        "status",
        "show",
        "list",
        "ls",
        "pwd",
        "whoami",
        "id",
        "uname",
        "cat /proc/version",
        "cat /proc/cpuinfo",
        "ps",
        "top",
        "free",
        "df",
        "mount",
        "ifconfig",
        "ip addr",
        "netstat",
        "route",
        "ping 8.8.8.8",
        "wget http://google.com",
        "curl http://google.com",
        "telnet 8.8.8.8 53",
        "nc 8.8.8.8 53",
        "ssh root@8.8.8.8",
        "ssh -o ConnectTimeout=1 root@8.8.8.8",
    ]
    
    for cmd in commands:
        response = send_command(ser, cmd, 3)
        
        # Check if we got actual output (not just echo)
        if response and response != cmd and len(response) > len(cmd):
            print(f"✅ Command '{cmd}' got response: {response[:100]}...")
            return True
    
    return False

def try_special_sequences(ser):
    """Try special sequences to wake up the camera"""
    print("\n⚡ Trying Special Wake-up Sequences...")
    print("=" * 50)
    
    # Try different wake-up sequences
    sequences = [
        # Multiple enters
        ['\r\n', '\r\n', '\r\n'],
        # Ctrl+C then enter
        ['\x03', '\r\n'],
        # Space then enter
        [' ', '\r\n'],
        # Tab then enter
        ['\t', '\r\n'],
        # Question mark
        ['?', '\r\n'],
        # Help command
        ['h', 'e', 'l', 'p', '\r\n'],
        # Version command
        ['v', 'e', 'r', 's', 'i', 'o', 'n', '\r\n'],
    ]
    
    for i, sequence in enumerate(sequences):
        print(f"Trying sequence {i+1}: {[repr(c) for c in sequence]}")
        
        for char in sequence:
            ser.write(char.encode())
            time.sleep(0.1)
        
        time.sleep(2)
        response = ser.read_all().decode(errors='ignore').strip()
        
        if response and len(response) > 10:
            print(f"✅ Sequence {i+1} got response: {response}")
            return True
        else:
            print(f"❌ Sequence {i+1} got no response")
    
    return False

def main():
    """Main function"""
    print("🔌 DCS-8000LH Direct USB Communication")
    print("=" * 60)
    print(f"Serial Port: {SERIAL_PORT}")
    print("")
    
    # Try different baud rates first
    working_baud = try_different_baud_rates()
    if working_baud:
        print(f"✅ Found working baud rate: {working_baud}")
        # Use the working baud rate
        ser = serial.Serial(SERIAL_PORT, working_baud, timeout=TIMEOUT)
    else:
        # Use default baud rate
        ser = connect_to_camera()
        if not ser:
            return
    
    try:
        # Clear any pending input/output
        ser.flushInput()
        ser.flushOutput()
        time.sleep(1)
        
        # Try boot interrupt
        if try_boot_interrupt(ser):
            print("✅ Boot interrupt successful!")
            return
        
        # Try special sequences
        if try_special_sequences(ser):
            print("✅ Special sequence successful!")
            return
        
        # Try direct commands
        if try_direct_commands(ser):
            print("✅ Direct commands successful!")
            return
        
        print("❌ All methods failed - camera not responding to commands")
        print("💡 Camera may need different approach or firmware")
        
    except KeyboardInterrupt:
        print("\n⚠️ Communication interrupted by user")
    except Exception as e:
        print(f"❌ Error during communication: {e}")
    finally:
        if ser:
            ser.close()
            print("🔌 USB connection closed")

if __name__ == "__main__":
    main()
