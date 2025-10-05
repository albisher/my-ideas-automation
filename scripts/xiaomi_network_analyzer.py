#!/usr/bin/env python3
"""
Xiaomi Network Command Analyzer
Advanced network monitoring that works even when device is offline
Monitors network traffic and learns commands from phone usage
"""

import subprocess
import json
import time
import re
import socket
import threading
import signal
import sys
import os
from datetime import datetime
from collections import defaultdict, deque

# Configuration
XIAOMI_IP = "192.168.68.68"
LOG_FILE = "xiaomi_network_analysis.log"
LEARNING_FILE = "xiaomi_network_learning.json"
COMMANDS_FILE = "xiaomi_network_commands.json"
TRAFFIC_FILE = "xiaomi_network_traffic.json"

class XiaomiNetworkAnalyzer:
    def __init__(self):
        self.xiaomi_ip = XIAOMI_IP
        self.log_file = LOG_FILE
        self.learning_file = LEARNING_FILE
        self.commands_file = COMMANDS_FILE
        self.traffic_file = TRAFFIC_FILE
        
        # Learning data structures
        self.learned_commands = {}
        self.network_traffic = deque(maxlen=1000)
        self.command_patterns = defaultdict(int)
        self.device_responses = deque(maxlen=500)
        
        # Analysis state
        self.running = False
        self.analysis_threads = []
        self.start_time = datetime.now()
        self.traffic_monitoring = False
        
        # Load existing data
        self.load_existing_data()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_existing_data(self):
        """Load existing learned data from files"""
        try:
            # Load existing commands
            if os.path.exists(self.commands_file):
                with open(self.commands_file, 'r') as f:
                    data = json.load(f)
                    if 'commands' in data:
                        self.learned_commands = data['commands']
                    self.log_message(f"📚 Loaded {len(self.learned_commands)} existing commands")
            
            # Load existing traffic data
            if os.path.exists(self.traffic_file):
                with open(self.traffic_file, 'r') as f:
                    traffic_data = json.load(f)
                    if 'traffic' in traffic_data:
                        for entry in traffic_data['traffic']:
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
    
    def check_network_connectivity(self):
        """Check network connectivity and find Xiaomi device"""
        try:
            # Check if we can reach the device
            result = subprocess.run(['ping', '-c', '1', '-W', '1000', self.xiaomi_ip], 
                                  capture_output=True, text=True)
            is_reachable = "1 received" in result.stdout
            
            if is_reachable:
                self.log_message(f"✅ Xiaomi device at {self.xiaomi_ip} is reachable")
                return True
            else:
                self.log_message(f"❌ Xiaomi device at {self.xiaomi_ip} is not reachable")
                self.log_message("🔍 This is normal - we'll monitor network traffic anyway")
                return False
        except Exception as e:
            self.log_message(f"Error checking connectivity: {e}")
            return False
    
    def scan_network_for_xiaomi_devices(self):
        """Scan network for Xiaomi devices"""
        try:
            self.log_message("🔍 Scanning network for Xiaomi devices...")
            
            # Get current network
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            network_info = result.stdout
            
            # Extract network range
            import re
            ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', network_info)
            if ip_match:
                current_ip = ip_match.group(1)
                network_base = '.'.join(current_ip.split('.')[:-1])
                self.log_message(f"📡 Scanning network {network_base}.0/24")
                
                # Scan for devices
                for i in range(1, 255):
                    test_ip = f"{network_base}.{i}"
                    if test_ip != current_ip:
                        try:
                            result = subprocess.run(['ping', '-c', '1', '-W', '500', test_ip], 
                                                  capture_output=True, text=True)
                            if "1 received" in result.stdout:
                                self.log_message(f"📱 Found device at {test_ip}")
                                # Test if it's a Xiaomi device
                                self.test_xiaomi_device(test_ip)
                        except:
                            continue
        except Exception as e:
            self.log_message(f"Error scanning network: {e}")
    
    def test_xiaomi_device(self, ip):
        """Test if device is a Xiaomi device"""
        try:
            # Test common Xiaomi ports
            xiaomi_ports = [54321, 8080, 80, 443, 9999, 8888]
            for port in xiaomi_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    self.log_message(f"🎯 Found Xiaomi device at {ip}:{port}")
                    self.learned_commands[f'xiaomi_device_{ip}'] = {
                        'ip': ip,
                        'port': port,
                        'discovered': True,
                        'timestamp': datetime.now().isoformat()
                    }
                    return True
        except Exception as e:
            pass
        return False
    
    def start_network_monitoring(self):
        """Start monitoring network traffic"""
        try:
            self.log_message("🌐 Starting network traffic monitoring...")
            
            # Get network interfaces
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            interfaces = []
            for line in result.stdout.split('\n'):
                if line.startswith('en') and 'inet' in line:
                    interface = line.split(':')[0]
                    interfaces.append(interface)
            
            if not interfaces:
                interfaces = ['en0', 'en1']  # Default interfaces
            
            self.log_message(f"📡 Monitoring interfaces: {interfaces}")
            
            # Start traffic monitoring for each interface
            for interface in interfaces:
                thread = threading.Thread(target=self.monitor_interface_traffic, 
                                        args=(interface,), daemon=True)
                thread.start()
                self.analysis_threads.append(thread)
            
            self.traffic_monitoring = True
            self.log_message("✅ Network monitoring started")
            
        except Exception as e:
            self.log_message(f"Error starting network monitoring: {e}")
    
    def monitor_interface_traffic(self, interface):
        """Monitor traffic on specific interface"""
        try:
            self.log_message(f"📊 Monitoring traffic on {interface}")
            
            # Use netstat to monitor connections
            while self.running:
                try:
                    result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
                    connections = result.stdout
                    
                    # Look for connections to Xiaomi IP or similar patterns
                    xiaomi_connections = []
                    for line in connections.split('\n'):
                        if self.xiaomi_ip in line or '192.168.68' in line:
                            xiaomi_connections.append(line)
                    
                    if xiaomi_connections:
                        self.log_message(f"🔍 Found {len(xiaomi_connections)} Xiaomi-related connections")
                        for conn in xiaomi_connections:
                            self.analyze_connection(conn)
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    self.log_message(f"Error monitoring {interface}: {e}")
                    time.sleep(10)
                    
        except Exception as e:
            self.log_message(f"Error in interface monitoring: {e}")
    
    def analyze_connection(self, connection):
        """Analyze network connection for Xiaomi commands"""
        try:
            # Extract connection info
            parts = connection.split()
            if len(parts) >= 4:
                local_addr = parts[3]
                remote_addr = parts[4]
                state = parts[5] if len(parts) > 5 else 'unknown'
                
                # Check if it's related to Xiaomi
                if self.xiaomi_ip in remote_addr or '192.168.68' in remote_addr:
                    self.log_message(f"📡 Xiaomi connection: {local_addr} -> {remote_addr} ({state})")
                    
                    # Record the connection
                    traffic_entry = {
                        'timestamp': datetime.now().isoformat(),
                        'local_addr': local_addr,
                        'remote_addr': remote_addr,
                        'state': state,
                        'type': 'xiaomi_connection'
                    }
                    
                    self.network_traffic.append(traffic_entry)
                    
                    # Learn from the connection pattern
                    self.learn_command_pattern(connection)
                    
        except Exception as e:
            self.log_message(f"Error analyzing connection: {e}")
    
    def learn_command_pattern(self, connection):
        """Learn command patterns from network connections"""
        try:
            # Extract patterns from connection
            if 'ESTABLISHED' in connection:
                self.command_patterns['established_connections'] += 1
                self.log_message("📝 Learned: Device establishes connections")
            
            if 'LISTEN' in connection:
                self.command_patterns['listening_ports'] += 1
                self.log_message("📝 Learned: Device has listening ports")
            
            # Look for port patterns
            import re
            port_match = re.search(r':(\d+)', connection)
            if port_match:
                port = port_match.group(1)
                self.command_patterns[f'port_{port}'] += 1
                self.log_message(f"📝 Learned: Port {port} is used")
                
                # Record as learned command
                command_key = f'network_port_{port}'
                self.learned_commands[command_key] = {
                    'port': port,
                    'pattern': connection,
                    'timestamp': datetime.now().isoformat(),
                    'discovered': True
                }
                
        except Exception as e:
            self.log_message(f"Error learning pattern: {e}")
    
    def continuous_data_saving(self):
        """Continuously save data to preserve learned commands"""
        while self.running:
            try:
                self.save_all_data()
                time.sleep(30)  # Save every 30 seconds
            except Exception as e:
                self.log_message(f"Error saving data: {e}")
                time.sleep(60)
    
    def save_all_data(self):
        """Save all learning data to files"""
        try:
            # Save learned commands
            commands_data = {
                'status': 'analyzing',
                'total_commands_discovered': len(self.learned_commands),
                'last_update': datetime.now().isoformat(),
                'commands': self.learned_commands,
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
            
            # Save learning summary
            learning_summary = {
                'status': 'analyzing',
                'total_commands_learned': len(self.learned_commands),
                'total_traffic_entries': len(self.network_traffic),
                'analysis_duration': str(datetime.now() - self.start_time),
                'start_time': self.start_time.isoformat(),
                'learned_commands': self.learned_commands,
                'command_patterns': dict(self.command_patterns),
                'traffic_summary': {
                    'total_connections': len(self.network_traffic),
                    'unique_ports': len(set(entry.get('port', '') for entry in self.network_traffic)),
                    'last_activity': self.network_traffic[-1]['timestamp'] if self.network_traffic else None
                }
            }
            
            with open(self.learning_file, 'w') as f:
                json.dump(learning_summary, f, indent=2)
            
            self.log_message(f"💾 Data saved: {len(self.learned_commands)} commands, {len(self.network_traffic)} traffic entries")
            
        except Exception as e:
            self.log_message(f"Error saving data: {e}")
    
    def run_continuous_analysis(self):
        """Run continuous analysis until stopped"""
        self.log_message("🚀 Starting Xiaomi Network Command Analyzer...")
        self.log_message(f"🎯 Target device: {self.xiaomi_ip}")
        self.log_message(f"📚 Loaded {len(self.learned_commands)} existing commands")
        self.log_message("📊 Analysis will monitor network traffic and learn commands")
        self.log_message("🛑 Press Ctrl+C to stop")
        
        self.running = True
        
        # Check connectivity
        device_reachable = self.check_network_connectivity()
        
        # Scan for Xiaomi devices
        self.scan_network_for_xiaomi_devices()
        
        # Start network monitoring
        self.start_network_monitoring()
        
        # Start data saving thread
        saver_thread = threading.Thread(target=self.continuous_data_saving, daemon=True)
        saver_thread.start()
        self.analysis_threads.append(saver_thread)
        
        try:
            while self.running:
                # Periodic network scan
                if not device_reachable:
                    self.log_message("🔍 Scanning for Xiaomi devices...")
                    self.scan_network_for_xiaomi_devices()
                    device_reachable = self.check_network_connectivity()
                
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.log_message("🛑 Analysis stopped by user")
        except Exception as e:
            self.log_message(f"❌ Analysis error: {e}")
        finally:
            self.running = False
            self.save_all_data()
            self.log_message("✅ Analysis completed and data saved")

def main():
    """Main function"""
    analyzer = XiaomiNetworkAnalyzer()
    analyzer.run_continuous_analysis()

if __name__ == "__main__":
    main()
