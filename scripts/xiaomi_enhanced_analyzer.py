#!/usr/bin/env python3
"""
Xiaomi Enhanced Command Analyzer
Enhanced version that properly updates and preserves learned commands
Runs continuously on local machine with better data persistence
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
XIAOMI_PORT = 54321
LOG_FILE = "xiaomi_enhanced_analysis.log"
LEARNING_FILE = "xiaomi_learning.json"
COMMANDS_FILE = "xiaomi_discovered_commands.json"
PROTOCOL_FILE = "xiaomi_protocol_analysis.json"
BACKUP_FILE = "xiaomi_backup.json"

class XiaomiEnhancedAnalyzer:
    def __init__(self):
        self.xiaomi_ip = XIAOMI_IP
        self.xiaomi_port = XIAOMI_PORT
        self.log_file = LOG_FILE
        self.learning_file = LEARNING_FILE
        self.commands_file = COMMANDS_FILE
        self.protocol_file = PROTOCOL_FILE
        self.backup_file = BACKUP_FILE
        
        # Learning data structures
        self.learned_commands = {}
        self.protocol_analysis = {}
        self.device_responses = deque(maxlen=1000)
        self.command_sequences = deque(maxlen=100)
        
        # Analysis state
        self.running = False
        self.analysis_threads = []
        self.last_activity = None
        self.device_online = False
        self.start_time = datetime.now()
        
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
            
            # Load existing protocol analysis
            if os.path.exists(self.protocol_file):
                with open(self.protocol_file, 'r') as f:
                    self.protocol_analysis = json.load(f)
                    self.log_message(f"📊 Loaded existing protocol analysis")
            
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
    
    def check_device_connectivity(self):
        """Check if Xiaomi device is reachable"""
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '1000', self.xiaomi_ip], 
                                  capture_output=True, text=True)
            is_online = "1 received" in result.stdout
            
            if is_online != self.device_online:
                self.device_online = is_online
                if is_online:
                    self.log_message(f"✅ Xiaomi device at {self.xiaomi_ip} is now ONLINE")
                    self.on_device_online()
                else:
                    self.log_message(f"❌ Xiaomi device at {self.xiaomi_ip} is now OFFLINE")
                    self.on_device_offline()
            
            return is_online
        except Exception as e:
            self.log_message(f"Error checking connectivity: {e}")
            return False
    
    def on_device_online(self):
        """Handle device coming online"""
        self.last_activity = datetime.now()
        self.start_analysis_threads()
        self.log_message("🔬 Starting comprehensive device analysis...")
    
    def on_device_offline(self):
        """Handle device going offline"""
        self.log_message("📡 Device offline, continuing to monitor...")
    
    def start_analysis_threads(self):
        """Start all analysis threads"""
        if not self.analysis_threads:
            # Port scanner thread
            port_thread = threading.Thread(target=self.continuous_port_scan, daemon=True)
            port_thread.start()
            self.analysis_threads.append(port_thread)
            
            # Command discoverer thread
            command_thread = threading.Thread(target=self.continuous_command_discovery, daemon=True)
            command_thread.start()
            self.analysis_threads.append(command_thread)
            
            # Data saver thread
            saver_thread = threading.Thread(target=self.continuous_data_saving, daemon=True)
            saver_thread.start()
            self.analysis_threads.append(saver_thread)
    
    def continuous_port_scan(self):
        """Continuously scan ports for changes"""
        known_ports = set()
        
        while self.running:
            try:
                if self.device_online:
                    current_ports = self.scan_ports()
                    
                    # Check for new ports
                    new_ports = current_ports - known_ports
                    if new_ports:
                        self.log_message(f"🔍 New ports discovered: {new_ports}")
                        self.analyze_new_ports(new_ports)
                    
                    known_ports = current_ports
                    self.protocol_analysis['open_ports'] = list(current_ports)
                    self.protocol_analysis['last_scan'] = datetime.now().isoformat()
                
                time.sleep(30)  # Scan every 30 seconds
            except Exception as e:
                self.log_message(f"Error in port scanning: {e}")
                time.sleep(60)
    
    def scan_ports(self):
        """Scan common Xiaomi ports"""
        common_ports = [54321, 8080, 80, 443, 22, 23, 554, 8554, 9999, 8888]
        open_ports = set()
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.xiaomi_ip, port))
                sock.close()
                
                if result == 0:
                    open_ports.add(port)
            except Exception:
                continue
        
        return open_ports
    
    def analyze_new_ports(self, ports):
        """Analyze newly discovered ports"""
        for port in ports:
            self.log_message(f"🔬 Analyzing port {port}...")
            self.test_http_on_port(port)
            self.test_udp_on_port(port)
            self.test_tcp_on_port(port)
    
    def test_http_on_port(self, port):
        """Test HTTP protocol on port"""
        try:
            result = subprocess.run([
                'curl', '-s', '-m', '3', f'http://{self.xiaomi_ip}:{port}/'
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                self.log_message(f"🌐 HTTP response on port {port}: {result.stdout[:200]}")
                command_key = f'http_port_{port}'
                self.learned_commands[command_key] = {
                    'protocol': 'HTTP',
                    'port': port,
                    'response': result.stdout[:500],
                    'timestamp': datetime.now().isoformat(),
                    'discovered': True
                }
                self.log_message(f"📝 Learned HTTP command: {command_key}")
        except Exception as e:
            pass
    
    def test_udp_on_port(self, port):
        """Test UDP protocol on port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            
            # Common Xiaomi UDP discovery packets
            discovery_packets = [
                b'\x21\x31\x00\x20\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff',
                b'{"id":1,"method":"miIO.info","params":[]}',
                b'{"method":"get_prop","params":["power","mode","temp"]}',
                b'{"method":"get_status","params":[]}'
            ]
            
            for packet in discovery_packets:
                sock.sendto(packet, (self.xiaomi_ip, port))
                time.sleep(0.5)
                
                try:
                    response, addr = sock.recvfrom(1024)
                    self.log_message(f"📡 UDP response on port {port}: {response.hex()}")
                    command_key = f'udp_port_{port}'
                    self.learned_commands[command_key] = {
                        'protocol': 'UDP',
                        'port': port,
                        'response': response.hex(),
                        'timestamp': datetime.now().isoformat(),
                        'discovered': True
                    }
                    self.log_message(f"📝 Learned UDP command: {command_key}")
                except socket.timeout:
                    continue
            
            sock.close()
        except Exception as e:
            pass
    
    def test_tcp_on_port(self, port):
        """Test TCP protocol on port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((self.xiaomi_ip, port))
            
            # Send common TCP probes
            probes = [
                b'GET / HTTP/1.1\r\nHost: ' + self.xiaomi_ip.encode() + b'\r\n\r\n',
                b'{"method":"info","params":[]}\r\n',
                b'STATUS\r\n'
            ]
            
            for probe in probes:
                sock.send(probe)
                time.sleep(0.5)
                
                try:
                    response = sock.recv(1024)
                    if response:
                        self.log_message(f"🔌 TCP response on port {port}: {response[:100]}")
                        command_key = f'tcp_port_{port}'
                        self.learned_commands[command_key] = {
                            'protocol': 'TCP',
                            'port': port,
                            'response': response.hex(),
                            'timestamp': datetime.now().isoformat(),
                            'discovered': True
                        }
                        self.log_message(f"📝 Learned TCP command: {command_key}")
                except socket.timeout:
                    continue
            
            sock.close()
        except Exception as e:
            pass
    
    def continuous_command_discovery(self):
        """Continuously discover new commands"""
        while self.running:
            try:
                if self.device_online:
                    self.discover_commands()
                time.sleep(60)  # Discover every minute
            except Exception as e:
                self.log_message(f"Error in command discovery: {e}")
                time.sleep(120)
    
    def discover_commands(self):
        """Discover new commands by testing common patterns"""
        # Test common Xiaomi IR commands
        ir_commands = [
            'power', 'volume_up', 'volume_down', 'channel_up', 'channel_down',
            'mute', 'menu', 'ok', 'back', 'up', 'down', 'left', 'right'
        ]
        
        for cmd in ir_commands:
            self.test_ir_command(cmd)
            time.sleep(1)  # Wait between commands
    
    def test_ir_command(self, command):
        """Test sending IR command"""
        try:
            # Try different command formats
            formats = [
                f'{{"method":"send_ir","params":["{command}"]}}',
                f'{{"method":"ir_{command}","params":[]}}',
                f'{{"method":"{command}","params":[]}}'
            ]
            
            for cmd_format in formats:
                self.send_udp_command(cmd_format.encode())
                time.sleep(0.5)
        except Exception as e:
            pass
    
    def send_udp_command(self, command):
        """Send UDP command to device"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            sock.sendto(command, (self.xiaomi_ip, self.xiaomi_port))
            
            try:
                response, addr = sock.recvfrom(1024)
                self.log_message(f"📡 Command response: {response.hex()}")
                self.device_responses.append({
                    'command': command.decode() if isinstance(command, bytes) else command,
                    'response': response.hex(),
                    'timestamp': datetime.now().isoformat()
                })
            except socket.timeout:
                pass
            
            sock.close()
        except Exception as e:
            pass
    
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
                'device_online': self.device_online,
                'total_commands_discovered': len(self.learned_commands),
                'last_update': datetime.now().isoformat(),
                'commands': self.learned_commands
            }
            
            with open(self.commands_file, 'w') as f:
                json.dump(commands_data, f, indent=2)
            
            # Save protocol analysis
            self.protocol_analysis['last_update'] = datetime.now().isoformat()
            with open(self.protocol_file, 'w') as f:
                json.dump(self.protocol_analysis, f, indent=2)
            
            # Save learning summary
            learning_summary = {
                'status': 'analyzing',
                'device_online': self.device_online,
                'total_commands_learned': len(self.learned_commands),
                'total_responses': len(self.device_responses),
                'analysis_duration': str(datetime.now() - self.start_time),
                'last_activity': self.last_activity.isoformat() if self.last_activity else None,
                'start_time': self.start_time.isoformat(),
                'learned_commands': self.learned_commands,
                'protocol_analysis': self.protocol_analysis
            }
            
            with open(self.learning_file, 'w') as f:
                json.dump(learning_summary, f, indent=2)
            
            # Create backup
            with open(self.backup_file, 'w') as f:
                json.dump(learning_summary, f, indent=2)
            
            self.log_message(f"💾 Data saved: {len(self.learned_commands)} commands, {len(self.device_responses)} responses")
            
        except Exception as e:
            self.log_message(f"Error saving data: {e}")
    
    def run_continuous_analysis(self):
        """Run continuous analysis until stopped"""
        self.log_message("🚀 Starting Xiaomi Enhanced Command Analyzer...")
        self.log_message(f"🎯 Target device: {self.xiaomi_ip}")
        self.log_message(f"📚 Loaded {len(self.learned_commands)} existing commands")
        self.log_message("📊 Analysis will run continuously until stopped")
        self.log_message("🛑 Press Ctrl+C to stop")
        
        self.running = True
        
        try:
            while self.running:
                # Check device connectivity
                self.check_device_connectivity()
                
                # Save data every 5 minutes
                if self.last_activity and (datetime.now() - self.last_activity).seconds > 300:
                    self.save_all_data()
                    self.last_activity = datetime.now()
                
                time.sleep(10)  # Check every 10 seconds
                
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
    analyzer = XiaomiEnhancedAnalyzer()
    analyzer.run_continuous_analysis()

if __name__ == "__main__":
    main()
