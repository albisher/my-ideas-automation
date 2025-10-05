#!/usr/bin/env python3
"""
Xiaomi Traffic Monitor
Monitors network traffic to capture commands sent to Xiaomi device
Works by monitoring network traffic regardless of device status
"""

import subprocess
import json
import time
import re
import threading
import signal
import sys
import os
from datetime import datetime
from collections import defaultdict, deque

# Configuration
XIAOMI_IP = "192.168.68.68"
LOG_FILE = "xiaomi_traffic_monitor.log"
COMMANDS_FILE = "xiaomi_captured_commands.json"
TRAFFIC_FILE = "xiaomi_network_traffic.json"

class XiaomiTrafficMonitor:
    def __init__(self):
        self.xiaomi_ip = XIAOMI_IP
        self.log_file = LOG_FILE
        self.commands_file = COMMANDS_FILE
        self.traffic_file = TRAFFIC_FILE
        
        # Data structures
        self.captured_commands = {}
        self.network_traffic = deque(maxlen=2000)
        self.command_patterns = defaultdict(int)
        self.traffic_monitoring = False
        
        # State
        self.running = False
        self.monitor_threads = []
        self.start_time = datetime.now()
        
        # Load existing data
        self.load_existing_data()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_existing_data(self):
        """Load existing captured data"""
        try:
            if os.path.exists(self.commands_file):
                with open(self.commands_file, 'r') as f:
                    data = json.load(f)
                    if 'commands' in data:
                        self.captured_commands = data['commands']
                    self.log_message(f"📚 Loaded {len(self.captured_commands)} existing commands")
            
            if os.path.exists(self.traffic_file):
                with open(self.traffic_file, 'r') as f:
                    data = json.load(f)
                    if 'traffic' in data:
                        for entry in data['traffic']:
                            self.network_traffic.append(entry)
                    self.log_message(f"📊 Loaded {len(self.network_traffic)} traffic entries")
            
            self.log_message("✅ Existing data loaded successfully")
        except Exception as e:
            self.log_message(f"⚠️ Could not load existing data: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.log_message(f"Received signal {signum}, shutting down...")
        self.running = False
        self.save_all_data()
        sys.exit(0)
    
    def log_message(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
    
    def get_network_interfaces(self):
        """Get available network interfaces"""
        try:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            interfaces = []
            for line in result.stdout.split('\n'):
                if line.startswith('en') and 'inet' in line:
                    interface = line.split(':')[0]
                    interfaces.append(interface)
            
            if not interfaces:
                interfaces = ['en0', 'en1']  # Default interfaces
            
            return interfaces
        except Exception as e:
            self.log_message(f"Error getting interfaces: {e}")
            return ['en0', 'en1']
    
    def start_traffic_monitoring(self):
        """Start monitoring network traffic"""
        try:
            self.log_message("🌐 Starting network traffic monitoring...")
            
            interfaces = self.get_network_interfaces()
            self.log_message(f"📡 Monitoring interfaces: {interfaces}")
            
            # Start monitoring each interface
            for interface in interfaces:
                thread = threading.Thread(target=self.monitor_interface, 
                                        args=(interface,), daemon=True)
                thread.start()
                self.monitor_threads.append(thread)
            
            # Start netstat monitoring
            netstat_thread = threading.Thread(target=self.monitor_netstat, daemon=True)
            netstat_thread.start()
            self.monitor_threads.append(netstat_thread)
            
            # Start lsof monitoring
            lsof_thread = threading.Thread(target=self.monitor_lsof, daemon=True)
            lsof_thread.start()
            self.monitor_threads.append(lsof_thread)
            
            self.traffic_monitoring = True
            self.log_message("✅ Traffic monitoring started")
            
        except Exception as e:
            self.log_message(f"Error starting traffic monitoring: {e}")
    
    def monitor_interface(self, interface):
        """Monitor traffic on specific interface"""
        try:
            self.log_message(f"📊 Monitoring traffic on {interface}")
            
            while self.running:
                try:
                    # Use netstat to monitor connections
                    result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
                    connections = result.stdout
                    
                    # Look for connections to Xiaomi IP
                    xiaomi_connections = []
                    for line in connections.split('\n'):
                        if self.xiaomi_ip in line:
                            xiaomi_connections.append(line)
                            self.analyze_connection(line)
                    
                    if xiaomi_connections:
                        self.log_message(f"🔍 Found {len(xiaomi_connections)} connections to {self.xiaomi_ip}")
                    
                    time.sleep(2)  # Check every 2 seconds
                    
                except Exception as e:
                    self.log_message(f"Error monitoring {interface}: {e}")
                    time.sleep(5)
                    
        except Exception as e:
            self.log_message(f"Error in interface monitoring: {e}")
    
    def monitor_netstat(self):
        """Monitor netstat for Xiaomi connections"""
        try:
            self.log_message("📊 Starting netstat monitoring...")
            
            while self.running:
                try:
                    # Get all connections
                    result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
                    connections = result.stdout
                    
                    # Look for Xiaomi-related connections
                    for line in connections.split('\n'):
                        if self.xiaomi_ip in line or '192.168.68' in line:
                            self.analyze_connection(line)
                    
                    time.sleep(3)  # Check every 3 seconds
                    
                except Exception as e:
                    self.log_message(f"Error in netstat monitoring: {e}")
                    time.sleep(10)
                    
        except Exception as e:
            self.log_message(f"Error in netstat monitoring: {e}")
    
    def monitor_lsof(self):
        """Monitor lsof for network connections"""
        try:
            self.log_message("📊 Starting lsof monitoring...")
            
            while self.running:
                try:
                    # Get network connections
                    result = subprocess.run(['lsof', '-i'], capture_output=True, text=True)
                    connections = result.stdout
                    
                    # Look for Xiaomi connections
                    for line in connections.split('\n'):
                        if self.xiaomi_ip in line:
                            self.analyze_lsof_connection(line)
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    self.log_message(f"Error in lsof monitoring: {e}")
                    time.sleep(10)
                    
        except Exception as e:
            self.log_message(f"Error in lsof monitoring: {e}")
    
    def analyze_connection(self, connection):
        """Analyze network connection for Xiaomi commands"""
        try:
            # Extract connection info
            parts = connection.split()
            if len(parts) >= 4:
                local_addr = parts[3]
                remote_addr = parts[4]
                state = parts[5] if len(parts) > 5 else 'unknown'
                
                # Record the connection
                traffic_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'local_addr': local_addr,
                    'remote_addr': remote_addr,
                    'state': state,
                    'type': 'netstat_connection',
                    'source': 'netstat'
                }
                
                self.network_traffic.append(traffic_entry)
                
                # Learn from the connection
                self.learn_from_connection(connection, traffic_entry)
                
                self.log_message(f"📡 Captured connection: {local_addr} -> {remote_addr} ({state})")
                
        except Exception as e:
            self.log_message(f"Error analyzing connection: {e}")
    
    def analyze_lsof_connection(self, connection):
        """Analyze lsof connection for Xiaomi commands"""
        try:
            # Extract connection info from lsof
            parts = connection.split()
            if len(parts) >= 9:
                process = parts[0]
                pid = parts[1]
                user = parts[2]
                fd = parts[3]
                type_info = parts[4]
                device = parts[5]
                size = parts[6]
                node = parts[7]
                name = parts[8]
                
                # Record the connection
                traffic_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'process': process,
                    'pid': pid,
                    'user': user,
                    'fd': fd,
                    'type': type_info,
                    'device': device,
                    'size': size,
                    'node': node,
                    'name': name,
                    'source': 'lsof'
                }
                
                self.network_traffic.append(traffic_entry)
                
                # Learn from the connection
                self.learn_from_lsof_connection(connection, traffic_entry)
                
                self.log_message(f"📱 Captured process connection: {process} ({pid}) -> {name}")
                
        except Exception as e:
            self.log_message(f"Error analyzing lsof connection: {e}")
    
    def learn_from_connection(self, connection, traffic_entry):
        """Learn from network connection"""
        try:
            # Extract port information
            if ':' in traffic_entry['remote_addr']:
                port = traffic_entry['remote_addr'].split(':')[-1]
                self.command_patterns[f'port_{port}'] += 1
                
                # Record as learned command
                command_key = f'network_port_{port}'
                self.captured_commands[command_key] = {
                    'port': port,
                    'connection': connection,
                    'timestamp': datetime.now().isoformat(),
                    'captured': True,
                    'type': 'network_port'
                }
                
                self.log_message(f"📝 Learned network port: {port}")
            
            # Learn connection patterns
            if 'ESTABLISHED' in connection:
                self.command_patterns['established_connections'] += 1
                self.log_message("📝 Learned: Established connections pattern")
            
            if 'LISTEN' in connection:
                self.command_patterns['listening_ports'] += 1
                self.log_message("📝 Learned: Listening ports pattern")
                
        except Exception as e:
            self.log_message(f"Error learning from connection: {e}")
    
    def learn_from_lsof_connection(self, connection, traffic_entry):
        """Learn from lsof connection"""
        try:
            # Extract process information
            process = traffic_entry['process']
            port = None
            
            # Extract port from name field
            if ':' in traffic_entry['name']:
                port = traffic_entry['name'].split(':')[-1]
            
            if port:
                self.command_patterns[f'process_{process}_port_{port}'] += 1
                
                # Record as learned command
                command_key = f'process_{process}_port_{port}'
                self.captured_commands[command_key] = {
                    'process': process,
                    'port': port,
                    'connection': connection,
                    'timestamp': datetime.now().isoformat(),
                    'captured': True,
                    'type': 'process_connection'
                }
                
                self.log_message(f"📝 Learned process connection: {process} on port {port}")
                
        except Exception as e:
            self.log_message(f"Error learning from lsof connection: {e}")
    
    def continuous_data_saving(self):
        """Continuously save data"""
        while self.running:
            try:
                self.save_all_data()
                time.sleep(30)  # Save every 30 seconds
            except Exception as e:
                self.log_message(f"Error saving data: {e}")
                time.sleep(60)
    
    def save_all_data(self):
        """Save all captured data"""
        try:
            # Save captured commands
            commands_data = {
                'status': 'monitoring',
                'total_commands_captured': len(self.captured_commands),
                'last_update': datetime.now().isoformat(),
                'commands': self.captured_commands,
                'command_patterns': dict(self.command_patterns)
            }
            
            with open(self.commands_file, 'w') as f:
                json.dump(commands_data, f, indent=2)
            
            # Save network traffic
            traffic_data = {
                'status': 'monitoring',
                'total_traffic_entries': len(self.network_traffic),
                'last_update': datetime.now().isoformat(),
                'traffic': list(self.network_traffic)
            }
            
            with open(self.traffic_file, 'w') as f:
                json.dump(traffic_data, f, indent=2)
            
            self.log_message(f"💾 Data saved: {len(self.captured_commands)} commands, {len(self.network_traffic)} traffic entries")
            
        except Exception as e:
            self.log_message(f"Error saving data: {e}")
    
    def run_continuous_monitoring(self):
        """Run continuous traffic monitoring"""
        self.log_message("🚀 Starting Xiaomi Traffic Monitor...")
        self.log_message(f"🎯 Monitoring traffic to: {self.xiaomi_ip}")
        self.log_message(f"📚 Loaded {len(self.captured_commands)} existing commands")
        self.log_message("📊 Will capture all network traffic to Xiaomi device")
        self.log_message("🛑 Press Ctrl+C to stop")
        
        self.running = True
        
        # Start traffic monitoring
        self.start_traffic_monitoring()
        
        # Start data saving thread
        saver_thread = threading.Thread(target=self.continuous_data_saving, daemon=True)
        saver_thread.start()
        self.monitor_threads.append(saver_thread)
        
        try:
            while self.running:
                # Show status every minute
                self.log_message(f"📊 Status: {len(self.captured_commands)} commands captured, {len(self.network_traffic)} traffic entries")
                time.sleep(60)
                
        except KeyboardInterrupt:
            self.log_message("🛑 Monitoring stopped by user")
        except Exception as e:
            self.log_message(f"❌ Monitoring error: {e}")
        finally:
            self.running = False
            self.save_all_data()
            self.log_message("✅ Monitoring completed and data saved")

def main():
    """Main function"""
    monitor = XiaomiTrafficMonitor()
    monitor.run_continuous_monitoring()

if __name__ == "__main__":
    main()
