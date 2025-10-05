#!/usr/bin/env python3
"""
Xiaomi Auto-Detector and Command Monitor
Automatically detects Xiaomi device IP using MAC address and monitors commands
"""

import subprocess
import time
import json
import datetime
import signal
import sys
import re
import threading
import os

# Configuration
PHONE_IP = "192.168.68.65"
XIAOMI_MAC = "D4-35-38-0A-BC-57"  # Your Xiaomi device MAC address
LOG_FILE = "xiaomi_auto_monitor.log"
COMMANDS_FILE = "xiaomi_auto_commands.json"
TRAFFIC_FILE = "xiaomi_auto_traffic.json"

# Global data
captured_commands = {
    'status': 'monitoring',
    'phone_ip': PHONE_IP,
    'xiaomi_mac': XIAOMI_MAC,
    'xiaomi_ip': None,
    'total_commands_captured': 0,
    'last_update': None,
    'commands': {},
    'command_patterns': {}
}

captured_traffic = {
    'status': 'monitoring',
    'total_traffic_entries': 0,
    'last_update': None,
    'traffic': []
}

def log_message(message, level='INFO'):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f'[{timestamp}] {level}: {message}\n')
    print(f'[{timestamp}] {level}: {message}')

def save_data():
    global captured_commands, captured_traffic
    captured_commands['last_update'] = datetime.datetime.now().isoformat()
    captured_traffic['last_update'] = datetime.datetime.now().isoformat()
    
    try:
        with open(COMMANDS_FILE, 'w') as f:
            json.dump(captured_commands, f, indent=2)
        with open(TRAFFIC_FILE, 'w') as f:
            json.dump(captured_traffic, f, indent=2)
        log_message(f'💾 Data saved: {captured_commands["total_commands_captured"]} commands, {captured_traffic["total_traffic_entries"]} traffic entries')
    except Exception as e:
        log_message(f'Error saving data: {e}')

def find_xiaomi_ip():
    """Find Xiaomi device IP using MAC address"""
    log_message(f'🔍 Searching for Xiaomi device with MAC: {XIAOMI_MAC}')
    
    try:
        # Use arp to find the device
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        arp_output = result.stdout
        
        # Look for the MAC address in ARP table
        for line in arp_output.split('\n'):
            if XIAOMI_MAC.upper() in line.upper() or XIAOMI_MAC.lower() in line.lower():
                # Extract IP from line like: "192.168.68.62 (192.168.68.62) at d4:35:38:0a:bc:57"
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if ip_match:
                    ip = ip_match.group(1)
                    log_message(f'✅ Found Xiaomi device at IP: {ip}')
                    return ip
        
        # If not in ARP table, try to ping the network and then check ARP again
        log_message('🔍 Device not in ARP table, scanning network...')
        
        # Ping the network to populate ARP table
        network_base = "192.168.68"
        for i in range(1, 255):
            ip = f"{network_base}.{i}"
            if ip != PHONE_IP:  # Don't ping our own phone
                try:
                    subprocess.run(['ping', '-c', '1', '-W', '1000', ip], 
                                capture_output=True, timeout=2)
                except:
                    pass
        
        # Check ARP table again
        time.sleep(2)
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        arp_output = result.stdout
        
        for line in arp_output.split('\n'):
            if XIAOMI_MAC.upper() in line.upper() or XIAOMI_MAC.lower() in line.lower():
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if ip_match:
                    ip = ip_match.group(1)
                    log_message(f'✅ Found Xiaomi device at IP: {ip}')
                    return ip
        
        log_message('❌ Xiaomi device not found in network')
        return None
        
    except Exception as e:
        log_message(f'Error finding Xiaomi device: {e}')
        return None

def test_connectivity(ip):
    """Test if we can reach the Xiaomi device"""
    try:
        result = subprocess.run(['ping', '-c', '1', ip], 
                              capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def start_monitoring(xiaomi_ip):
    """Start monitoring traffic between phone and Xiaomi device"""
    log_message(f'🚀 Starting traffic monitoring...')
    log_message(f'📱 Phone: {PHONE_IP}')
    log_message(f'🎯 Xiaomi: {xiaomi_ip}')
    
    # Update global data
    captured_commands['xiaomi_ip'] = xiaomi_ip
    
    try:
        # Start tcpdump with specific filter
        tcpdump_filter = f'host {PHONE_IP} and host {xiaomi_ip}'
        log_message(f'🔍 Running: sudo tcpdump -i en1 -n -l -A -s 0 {tcpdump_filter}')
        
        process = subprocess.Popen(
            ['sudo', 'tcpdump', '-i', 'en1', '-n', '-l', '-A', '-s', '0', tcpdump_filter],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        log_message('✅ tcpdump monitoring started')
        log_message('📊 Reading tcpdump output...')
        log_message('🎯 NOW SEND COMMANDS FROM YOUR PHONE!')
        
        last_save_time = time.time()
        
        while True:
            line = process.stdout.readline()
            if not line:
                break
            
            timestamp = datetime.datetime.now().isoformat()
            traffic_entry = {
                'timestamp': timestamp,
                'packet_data': line.strip(),
                'source': 'tcpdump'
            }
            captured_traffic['traffic'].append(traffic_entry)
            captured_traffic['total_traffic_entries'] += 1
            
            # Check for phone to Xiaomi traffic
            if PHONE_IP in line and xiaomi_ip in line:
                log_message(f'📱 DETECTED: Phone -> Xiaomi traffic: {line.strip()}')
                
                # Extract port information
                port_match = re.search(r'(\d+\.\d+\.\d+\.\d+)\.(\d+).*?(\d+\.\d+\.\d+\.\d+)\.(\d+)', line)
                if port_match:
                    src_ip, src_port, dst_ip, dst_port = port_match.groups()
                    if src_ip == PHONE_IP and dst_ip == xiaomi_ip:
                        command_key = f'phone_to_xiaomi_{dst_port}'
                        captured_commands['commands'][command_key] = {
                            'src_ip': src_ip,
                            'dst_ip': dst_ip,
                            'src_port': src_port,
                            'dst_port': dst_port,
                            'timestamp': timestamp,
                            'captured': True,
                            'type': 'phone_to_xiaomi'
                        }
                        captured_commands['total_commands_captured'] += 1
                        captured_commands['command_patterns'][f'port_{dst_port}'] = captured_commands['command_patterns'].get(f'port_{dst_port}', 0) + 1
                        log_message(f'📝 LEARNED COMMAND: {command_key}')
                        save_data()  # Save immediately when command is learned
            
            # Save data every 10 seconds
            if time.time() - last_save_time >= 10:
                save_data()
                last_save_time = time.time()
                
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log_message(f'Error during monitoring: {e}')
    finally:
        if 'process' in locals() and process.poll() is None:
            process.terminate()
            process.wait()
        save_data()

def signal_handler(sig, frame):
    log_message('🛑 Received signal, shutting down...')
    save_data()
    log_message('✅ Monitoring completed and data saved')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    log_message('🚀 Starting Xiaomi Auto-Detector and Command Monitor...')
    log_message(f'📱 Monitoring phone: {PHONE_IP}')
    log_message(f'🔍 Looking for Xiaomi device with MAC: {XIAOMI_MAC}')
    
    # Find Xiaomi device IP
    xiaomi_ip = find_xiaomi_ip()
    
    if not xiaomi_ip:
        log_message('❌ Could not find Xiaomi device on network')
        log_message('💡 Make sure your Xiaomi device is connected to the same network')
        return
    
    # Test connectivity
    if not test_connectivity(xiaomi_ip):
        log_message(f'⚠️  Xiaomi device found at {xiaomi_ip} but not responding to ping')
        log_message('💡 This is normal - some devices don\'t respond to ping but still work')
    
    # Start monitoring
    log_message('🛑 Press Ctrl+C to stop')
    start_monitoring(xiaomi_ip)

if __name__ == "__main__":
    main()
