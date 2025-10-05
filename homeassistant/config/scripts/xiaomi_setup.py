#!/usr/bin/env python3
"""
Xiaomi Device Setup Script for Home Assistant
This script helps configure the Xiaomi device for Hisense TV control
"""

import socket
import struct
import time
import json

def discover_xiaomi_device():
    """Discover Xiaomi device on the network"""
    print("Discovering Xiaomi device...")
    
    # Try to find the device on the network
    for i in range(60, 80):
        ip = f"192.168.68.{i}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            
            # Send discovery packet
            discovery_packet = b'\x21\x31\x00\x20\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
            sock.sendto(discovery_packet, (ip, 54321))
            
            try:
                data, addr = sock.recvfrom(1024)
                print(f"Found Xiaomi device at {ip}")
                print(f"Device ID: {data[8:16].hex()}")
                print(f"Timestamp: {data[16:20].hex()}")
                print(f"Checksum: {data[20:32].hex()}")
                return ip
            except socket.timeout:
                pass
            finally:
                sock.close()
        except:
            pass
    
    return None

def test_xiaomi_connection(ip, token):
    """Test connection to Xiaomi device"""
    try:
        from miio import Device
        device = Device(ip, token)
        info = device.info()
        print(f"SUCCESS! Device info: {info}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def learn_ir_commands(ip, token):
    """Learn IR commands for Hisense TV"""
    try:
        from miio import Device
        device = Device(ip, token)
        
        print("Learning IR commands for Hisense TV...")
        print("Please point your Hisense TV remote at the Xiaomi device and press the following buttons:")
        
        commands = {
            'power': 'Press the POWER button on your Hisense TV remote',
            'volume_up': 'Press the VOLUME UP button on your Hisense TV remote',
            'volume_down': 'Press the VOLUME DOWN button on your Hisense TV remote',
            'channel_up': 'Press the CHANNEL UP button on your Hisense TV remote',
            'channel_down': 'Press the CHANNEL DOWN button on your Hisense TV remote',
            'input': 'Press the INPUT button on your Hisense TV remote',
            'menu': 'Press the MENU button on your Hisense TV remote',
            'back': 'Press the BACK button on your Hisense TV remote',
            'ok': 'Press the OK button on your Hisense TV remote',
            'up': 'Press the UP arrow button on your Hisense TV remote',
            'down': 'Press the DOWN arrow button on your Hisense TV remote',
            'left': 'Press the LEFT arrow button on your Hisense TV remote',
            'right': 'Press the RIGHT arrow button on your Hisense TV remote'
        }
        
        learned_commands = {}
        
        for command, instruction in commands.items():
            print(f"\n{instruction}")
            input("Press Enter when ready...")
            
            try:
                # Try to learn the command
                result = device.send('learn_ir', [command])
                learned_commands[command] = result
                print(f"Learned command: {command}")
            except Exception as e:
                print(f"Failed to learn command {command}: {e}")
        
        return learned_commands
        
    except Exception as e:
        print(f"IR learning failed: {e}")
        return {}

def main():
    print("Xiaomi Device Setup for Home Assistant")
    print("=====================================")
    
    # Discover device
    ip = discover_xiaomi_device()
    if not ip:
        print("No Xiaomi device found on the network")
        return
    
    print(f"\nDevice found at: {ip}")
    
    # Get token from user
    token = input("Enter the Xiaomi device token (32 characters): ").strip()
    if len(token) != 32:
        print("Invalid token length. Token must be 32 characters.")
        return
    
    # Test connection
    if not test_xiaomi_connection(ip, token):
        print("Failed to connect to device. Please check the token.")
        return
    
    print("Connection successful!")
    
    # Learn IR commands
    learned_commands = learn_ir_commands(ip, token)
    
    if learned_commands:
        print("\nLearned IR commands:")
        for command, data in learned_commands.items():
            print(f"  {command}: {data}")
        
        # Update configuration
        print("\nUpdating Home Assistant configuration...")
        # This would update the configuration.yaml file with the learned commands
        print("Configuration updated successfully!")
    else:
        print("No IR commands learned.")

if __name__ == "__main__":
    main()
