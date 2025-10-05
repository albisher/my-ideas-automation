#!/usr/bin/env python3
"""
Network Monitor for Xiaomi Device Commands
Monitors network traffic to 192.168.68.68 and logs commands from phone
"""

import subprocess
import json
import time
import re
from datetime import datetime
import os

# Configuration
XIAOMI_IP = "192.168.68.68"
LOG_FILE = "/config/network_monitor.log"
STATE_FILE = "/config/network_state.json"

def get_network_interfaces():
    """Get available network interfaces"""
    try:
        result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
        interfaces = []
        for line in result.stdout.split('\n'):
            if ': ' in line and 'state' in line:
                interface = line.split(':')[1].strip()
                # Skip loopback and tunnel interfaces
                if (interface != 'lo' and 
                    not interface.startswith('tun') and 
                    not interface.startswith('gre') and
                    not interface.startswith('sit') and
                    not interface.startswith('ip6') and
                    not interface.startswith('erspan')):
                    interfaces.append(interface)
        return interfaces
    except Exception as e:
        print(f"Error getting interfaces: {e}")
        return ['eth0', 'eth1']  # Default fallback for Docker

def monitor_tcpdump():
    """Monitor network traffic using tcpdump"""
    interfaces = get_network_interfaces()
    
    for interface in interfaces:
        try:
            # Monitor traffic to Xiaomi device
            cmd = [
                'tcpdump', '-i', interface, '-n', 
                f'host {XIAOMI_IP}', '-l', '-q'
            ]
            
            print(f"Starting tcpdump on interface {interface}")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, text=True)
            
            while True:
                output = process.stdout.readline()
                if output:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_entry = f"[{timestamp}] {interface}: {output.strip()}"
                    
                    # Log the entry
                    with open(LOG_FILE, 'a') as f:
                        f.write(log_entry + '\n')
                    
                    # Update state file
                    update_state(interface, output.strip())
                    
                    print(log_entry)
                
                if process.poll() is not None:
                    break
                    
        except Exception as e:
            print(f"Error monitoring interface {interface}: {e}")
            continue

def update_state(interface, data):
    """Update the state file with latest network activity"""
    try:
        state = {
            'last_activity': datetime.now().isoformat(),
            'interface': interface,
            'data': data,
            'xiaomi_ip': XIAOMI_IP,
            'status': 'active'
        }
        
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
            
    except Exception as e:
        print(f"Error updating state: {e}")

def get_network_stats():
    """Get network statistics"""
    try:
        # Get network interface statistics
        result = subprocess.run(['cat', '/proc/net/dev'], capture_output=True, text=True)
        
        stats = {}
        for line in result.stdout.split('\n')[2:]:  # Skip header lines
            if ':' in line:
                parts = line.split(':')
                interface = parts[0].strip()
                data = parts[1].split()
                
                if len(data) >= 9:
                    stats[interface] = {
                        'rx_bytes': int(data[0]),
                        'rx_packets': int(data[1]),
                        'tx_bytes': int(data[8]),
                        'tx_packets': int(data[9])
                    }
        
        return stats
    except Exception as e:
        print(f"Error getting network stats: {e}")
        return {}

def check_xiaomi_connectivity():
    """Check if Xiaomi device is reachable"""
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '1', XIAOMI_IP], 
                              capture_output=True, text=True)
        return "1 received" in result.stdout
    except Exception as e:
        print(f"Error checking connectivity: {e}")
        return False

def main():
    """Main monitoring function"""
    print(f"Starting network monitor for Xiaomi device at {XIAOMI_IP}")
    print(f"Log file: {LOG_FILE}")
    print(f"State file: {STATE_FILE}")
    
    # Initialize state file
    if not os.path.exists(STATE_FILE):
        initial_state = {
            'last_activity': datetime.now().isoformat(),
            'interface': 'unknown',
            'data': 'Initialized',
            'xiaomi_ip': XIAOMI_IP,
            'status': 'initializing'
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(initial_state, f, indent=2)
    
    # Check initial connectivity
    if check_xiaomi_connectivity():
        print(f"Xiaomi device at {XIAOMI_IP} is reachable")
    else:
        print(f"Warning: Xiaomi device at {XIAOMI_IP} is not reachable")
    
    # Start monitoring
    try:
        monitor_tcpdump()
    except KeyboardInterrupt:
        print("\nStopping network monitor...")
    except Exception as e:
        print(f"Error in main monitoring: {e}")

if __name__ == "__main__":
    main()
