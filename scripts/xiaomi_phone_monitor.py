#!/usr/bin/env python3
"""
Xiaomi Phone Traffic Monitor
Monitors network traffic specifically from phone to Xiaomi device
Uses tcpdump to capture packets between specific IPs
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
PHONE_IP = "192.168.68.65"
XIAOMI_IP = "192.168.68.68"
LOG_FILE = "xiaomi_phone_monitor.log"
COMMANDS_FILE = "xiaomi_phone_commands.json"
TRAFFIC_FILE = "xiaomi_phone_traffic.json"

class XiaomiPhoneMonitor:
    def __init__(self):
        self.phone_ip = PHONE_IP
        self.xiaomi_ip = XIAOMI_IP
        self.log_file = LOG_FILE
        self.commands_file = COMMANDS_FILE
        self.traffic_file = TRAFFIC_FILE
        
        # Data structures
        self.captured_commands = {}
        self.network_traffic = deque(maxlen=1000)
        self.command_patterns = defaultdict(int)
        self.tcpdump_process = None
        
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
        if self.tcpdump_process:
            self.tcpdump_process.terminate()
        self.save_all_data()
        sys.exit(0)
    
    def log_message(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
    
    def get_network_interface(self):
        """Get the network interface for monitoring"""
        try:
            # Get default route interface
            result = subprocess.run(['route', 'get', 'default'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'interface:' in line:
                    interface = line.split(':')[1].strip()
                    self.log_message(f"📡 Using interface: {interface}")
                    return interface
            
            # Fallback to common interfaces
            interfaces = ['en0', 'en1', 'wlan0', 'eth0']
            for interface in interfaces:
                try:
                    result = subprocess.run(['ifconfig', interface], capture_output=True, text=True)
                    if 'inet' in result.stdout:
                        self.log_message(f"📡 Using fallback interface: {interface}")
                        return interface
                except:
                    continue
            
            return 'en0'  # Default fallback
        except Exception as e:
            self.log_message(f"Error getting interface: {e}")
            return 'en0'
    
    def start_tcpdump_monitoring(self):
        """Start tcpdump to monitor traffic between phone and Xiaomi"""
        try:
            interface = self.get_network_interface()
            self.log_message(f"🌐 Starting tcpdump monitoring on {interface}")
            
            # Create tcpdump filter for traffic between phone and Xiaomi
            filter_expr = f"host {self.phone_ip} and host {self.xiaomi_ip}"
            
            # Start tcpdump process
            cmd = [
                'sudo', 'tcpdump', 
                '-i', interface,
                '-n',  # Don't resolve hostnames
                '-l',  # Line buffered
                '-A',  # Print ASCII
                '-s', '0',  # Capture full packets
                filter_expr
            ]
            
            self.log_message(f"🔍 Running: {' '.join(cmd)}")
            self.log_message(f"📡 Filter: {filter_expr}")
            
            self.tcpdump_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Start thread to read tcpdump output
            monitor_thread = threading.Thread(target=self.read_tcpdump_output, daemon=True)
            monitor_thread.start()
            self.monitor_threads.append(monitor_thread)
            
            self.log_message("✅ tcpdump monitoring started")
            
        except Exception as e:
            self.log_message(f"Error starting tcpdump: {e}")
            self.log_message("💡 Make sure tcpdump is installed: brew install tcpdump")
    
    def read_tcpdump_output(self):
        """Read and process tcpdump output"""
        try:
            self.log_message("📊 Reading tcpdump output...")
            
            while self.running and self.tcpdump_process:
                try:
                    line = self.tcpdump_process.stdout.readline()
                    if line:
                        self.process_tcpdump_line(line)
                    else:
                        break
                except Exception as e:
                    self.log_message(f"Error reading tcpdump: {e}")
                    break
                    
        except Exception as e:
            self.log_message(f"Error in tcpdump reader: {e}")
    
    def process_tcpdump_line(self, line):
        """Process a line from tcpdump output"""
        try:
            # Parse tcpdump output
            if 'IP' in line and (self.phone_ip in line or self.xiaomi_ip in line):
                self.log_message(f"📡 Captured packet: {line.strip()}")
                
                # Extract packet information
                packet_info = self.parse_tcpdump_line(line)
                if packet_info:
                    self.network_traffic.append(packet_info)
                    self.analyze_packet(packet_info)
                    
        except Exception as e:
            self.log_message(f"Error processing tcpdump line: {e}")
    
    def parse_tcpdump_line(self, line):
        """Parse tcpdump line to extract packet information"""
        try:
            # Extract timestamp
            timestamp_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d+)', line)
            timestamp = timestamp_match.group(1) if timestamp_match else datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            # Extract source and destination
            ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)\.(\d+) > (\d+\.\d+\.\d+\.\d+)\.(\d+)', line)
            if ip_match:
                src_ip, src_port, dst_ip, dst_port = ip_match.groups()
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'src_ip': src_ip,
                    'src_port': src_port,
                    'dst_ip': dst_ip,
                    'dst_port': dst_port,
                    'raw_line': line.strip(),
                    'type': 'tcpdump_packet'
                }
            
            return None
            
        except Exception as e:
            self.log_message(f"Error parsing tcpdump line: {e}")
            return None
    
    def analyze_packet(self, packet_info):
        """Analyze packet for Xiaomi commands"""
        try:
            src_ip = packet_info['src_ip']
            dst_ip = packet_info['dst_ip']
            src_port = packet_info['src_port']
            dst_port = packet_info['dst_port']
            
            # Check if it's from phone to Xiaomi
            if src_ip == self.phone_ip and dst_ip == self.xiaomi_ip:
                self.log_message(f"📱 Phone -> Xiaomi: {src_ip}:{src_port} -> {dst_ip}:{dst_port}")
                
                # Learn from the connection
                command_key = f'phone_to_xiaomi_{dst_port}'
                self.captured_commands[command_key] = {
                    'src_ip': src_ip,
                    'dst_ip': dst_ip,
                    'src_port': src_port,
                    'dst_port': dst_port,
                    'timestamp': packet_info['timestamp'],
                    'captured': True,
                    'type': 'phone_to_xiaomi'
                }
                
                self.command_patterns[f'port_{dst_port}'] += 1
                self.log_message(f"📝 Learned command: {command_key}")
                # Save immediately when new command is learned
                self.save_all_data()
            
            # Check if it's from Xiaomi to phone
            elif src_ip == self.xiaomi_ip and dst_ip == self.phone_ip:
                self.log_message(f"📱 Xiaomi -> Phone: {src_ip}:{src_port} -> {dst_ip}:{dst_port}")
                
                # Learn from the response
                command_key = f'xiaomi_to_phone_{src_port}'
                self.captured_commands[command_key] = {
                    'src_ip': src_ip,
                    'dst_ip': dst_ip,
                    'src_port': src_port,
                    'dst_port': dst_port,
                    'timestamp': packet_info['timestamp'],
                    'captured': True,
                    'type': 'xiaomi_to_phone'
                }
                
                self.command_patterns[f'response_port_{src_port}'] += 1
                self.log_message(f"📝 Learned response: {command_key}")
                # Save immediately when new response is learned
                self.save_all_data()
                
        except Exception as e:
            self.log_message(f"Error analyzing packet: {e}")
    
    def continuous_data_saving(self):
        """Continuously save data"""
        while self.running:
            try:
                self.save_all_data()
                time.sleep(10)  # Save every 10 seconds for immediate updates
            except Exception as e:
                self.log_message(f"Error saving data: {e}")
                time.sleep(30)
    
    def save_all_data(self):
        """Save all captured data"""
        try:
            # Save captured commands
            commands_data = {
                'status': 'monitoring',
                'phone_ip': self.phone_ip,
                'xiaomi_ip': self.xiaomi_ip,
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
        """Run continuous phone-to-Xiaomi monitoring"""
        self.log_message("🚀 Starting Xiaomi Phone Traffic Monitor...")
        self.log_message(f"📱 Monitoring phone: {self.phone_ip}")
        self.log_message(f"🎯 Monitoring Xiaomi: {self.xiaomi_ip}")
        self.log_message(f"📚 Loaded {len(self.captured_commands)} existing commands")
        self.log_message("📊 Will capture ONLY traffic between phone and Xiaomi device")
        self.log_message("🛑 Press Ctrl+C to stop")
        
        self.running = True
        
        # Start tcpdump monitoring
        self.start_tcpdump_monitoring()
        
        # Start data saving thread
        saver_thread = threading.Thread(target=self.continuous_data_saving, daemon=True)
        saver_thread.start()
        self.monitor_threads.append(saver_thread)
        
        try:
            while self.running:
                # Show status every 30 seconds and save immediately
                self.log_message(f"📊 Status: {len(self.captured_commands)} commands captured, {len(self.network_traffic)} traffic entries")
                self.save_all_data()  # Save immediately on each status update
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            self.log_message("🛑 Monitoring stopped by user")
        except Exception as e:
            self.log_message(f"❌ Monitoring error: {e}")
        finally:
            self.running = False
            if self.tcpdump_process:
                self.tcpdump_process.terminate()
            self.save_all_data()
            self.log_message("✅ Monitoring completed and data saved")

def main():
    """Main function"""
    monitor = XiaomiPhoneMonitor()
    monitor.run_continuous_monitoring()

if __name__ == "__main__":
    main()
