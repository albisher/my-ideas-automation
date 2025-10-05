#!/usr/bin/env python3
"""
Xiaomi Connection Monitor
Monitors network connections without requiring sudo privileges
"""

import subprocess
import time
import json
import datetime
import signal
import sys
import re
import threading

# Configuration
PHONE_IP = "192.168.68.65"
XIAOMI_IP = "192.168.68.62"
LOG_FILE = "xiaomi_connection_monitor.log"
CONNECTIONS_FILE = "xiaomi_connections.json"
COMMANDS_FILE = "xiaomi_learned_commands.json"

# Global data
captured_connections = {
    'status': 'monitoring',
    'phone_ip': PHONE_IP,
    'xiaomi_ip': XIAOMI_IP,
    'total_connections': 0,
    'last_update': None,
    'connections': [],
    'learned_commands': {}
}

def log_message(message, level='INFO'):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f'[{timestamp}] {level}: {message}\n')
    print(f'[{timestamp}] {level}: {message}')

def save_data():
    global captured_connections
    captured_connections['last_update'] = datetime.datetime.now().isoformat()
    
    try:
        with open(CONNECTIONS_FILE, 'w') as f:
            json.dump(captured_connections, f, indent=2)
        with open(COMMANDS_FILE, 'w') as f:
            json.dump(captured_connections['learned_commands'], f, indent=2)
        log_message(f'💾 Data saved: {captured_connections["total_connections"]} connections captured')
    except Exception as e:
        log_message(f'Error saving data: {e}')

def monitor_connections():
    """Monitor network connections using netstat"""
    log_message('🔍 Starting connection monitoring...')
    
    try:
        while True:
            # Get current connections
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
            netstat_output = result.stdout
            
            # Look for connections between phone and Xiaomi
            connections_found = []
            for line in netstat_output.split('\n'):
                if PHONE_IP in line and XIAOMI_IP in line:
                    connections_found.append(line.strip())
                    log_message(f'📱 DETECTED CONNECTION: {line.strip()}')
            
            if connections_found:
                timestamp = datetime.datetime.now().isoformat()
                connection_entry = {
                    'timestamp': timestamp,
                    'connections': connections_found,
                    'source': 'netstat'
                }
                captured_connections['connections'].append(connection_entry)
                captured_connections['total_connections'] += 1
                
                # Try to extract port information
                for conn in connections_found:
                    port_match = re.search(r'(\d+\.\d+\.\d+\.\d+)\.(\d+).*?(\d+\.\d+\.\d+\.\d+)\.(\d+)', conn)
                    if port_match:
                        src_ip, src_port, dst_ip, dst_port = port_match.groups()
                        if src_ip == PHONE_IP and dst_ip == XIAOMI_IP:
                            command_key = f'phone_to_xiaomi_{dst_port}'
                            captured_connections['learned_commands'][command_key] = {
                                'src_ip': src_ip,
                                'dst_ip': dst_ip,
                                'src_port': src_port,
                                'dst_port': dst_port,
                                'timestamp': timestamp,
                                'captured': True,
                                'type': 'phone_to_xiaomi'
                            }
                            log_message(f'📝 LEARNED COMMAND: {command_key}')
                            save_data()  # Save immediately when command is learned
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log_message(f'Error during monitoring: {e}')

def monitor_processes():
    """Monitor processes that might be communicating with Xiaomi device"""
    log_message('🔍 Starting process monitoring...')
    
    try:
        while True:
            # Get processes with network connections
            result = subprocess.run(['lsof', '-i'], capture_output=True, text=True)
            lsof_output = result.stdout
            
            # Look for processes connecting to Xiaomi IP
            xiaomi_processes = []
            for line in lsof_output.split('\n'):
                if XIAOMI_IP in line:
                    xiaomi_processes.append(line.strip())
                    log_message(f'🔍 PROCESS CONNECTING TO XIAOMI: {line.strip()}')
            
            if xiaomi_processes:
                timestamp = datetime.datetime.now().isoformat()
                process_entry = {
                    'timestamp': timestamp,
                    'processes': xiaomi_processes,
                    'source': 'lsof'
                }
                captured_connections['connections'].append(process_entry)
                captured_connections['total_connections'] += 1
                save_data()
            
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log_message(f'Error during process monitoring: {e}')

def signal_handler(sig, frame):
    log_message('🛑 Received signal, shutting down...')
    save_data()
    log_message('✅ Monitoring completed and data saved')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    log_message('🚀 Starting Xiaomi Connection Monitor...')
    log_message(f'📱 Monitoring phone: {PHONE_IP}')
    log_message(f'🎯 Monitoring Xiaomi: {XIAOMI_IP}')
    log_message('📊 Will monitor network connections and processes')
    log_message('🛑 Press Ctrl+C to stop')
    
    # Start monitoring in separate threads
    connection_thread = threading.Thread(target=monitor_connections)
    process_thread = threading.Thread(target=monitor_processes)
    
    connection_thread.start()
    process_thread.start()
    
    try:
        while True:
            log_message(f'📊 Status: {captured_connections["total_connections"]} connections captured')
            time.sleep(30)  # Status update every 30 seconds
    except KeyboardInterrupt:
        pass
    finally:
        connection_thread.join()
        process_thread.join()
        save_data()

if __name__ == "__main__":
    main()
