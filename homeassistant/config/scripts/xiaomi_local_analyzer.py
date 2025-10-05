#!/usr/bin/env python3
"""
Xiaomi Local Command Analyzer
Runs continuously on local machine to learn Xiaomi device commands and protocols
Provides deep analysis and learning capabilities
"""

import subprocess
import json
import time
import re
import socket
import threading
import signal
import sys
from datetime import datetime
from collections import defaultdict, deque
import os

# Configuration
XIAOMI_IP = "192.168.68.68"
XIAOMI_PORT = 54321
LOG_FILE = "/config/xiaomi_local_analysis.log"
LEARNING_FILE = "/config/xiaomi_learning.json"
PATTERNS_FILE = "/config/xiaomi_patterns.json"
COMMANDS_FILE = "/config/xiaomi_discovered_commands.json"
PROTOCOL_FILE = "/config/xiaomi_protocol_analysis.json"

class XiaomiLocalAnalyzer:
    def __init__(self):
        self.xiaomi_ip = XIAOMI_IP
        self.xiaomi_port = XIAOMI_PORT
        self.log_file = LOG_FILE
        self.learning_file = LEARNING_FILE
        self.patterns_file = PATTERNS_FILE
        self.commands_file = COMMANDS_FILE
        self.protocol_file = PROTOCOL_FILE
        
        # Learning data structures
        self.learned_commands = {}
        self.communication_patterns = defaultdict(list)
        self.protocol_analysis = {}
        self.device_responses = deque(maxlen=1000)
        self.command_sequences = deque(maxlen=100)
        
        # Analysis state
        self.running = False
        self.analysis_threads = []
        self.last_activity = None
        self.device_online = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.log_message(f"Received signal {signum}, shutting down...")
        self.running = False
        self.save_learning_data()
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
            result = subprocess.run(['ping', '-c', '1', '-W', '1', self.xiaomi_ip], 
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
        self.log_message("Starting comprehensive device analysis...")
    
    def on_device_offline(self):
        """Handle device going offline"""
        self.log_message("Device offline, continuing to monitor...")
    
    def start_analysis_threads(self):
        """Start all analysis threads"""
        if not self.analysis_threads:
            # Port scanner thread
            port_thread = threading.Thread(target=self.continuous_port_scan, daemon=True)
            port_thread.start()
            self.analysis_threads.append(port_thread)
            
            # Traffic analyzer thread
            traffic_thread = threading.Thread(target=self.continuous_traffic_analysis, daemon=True)
            traffic_thread.start()
            self.analysis_threads.append(traffic_thread)
            
            # Command discoverer thread
            command_thread = threading.Thread(target=self.continuous_command_discovery, daemon=True)
            command_thread.start()
            self.analysis_threads.append(command_thread)
            
            # Protocol analyzer thread
            protocol_thread = threading.Thread(target=self.continuous_protocol_analysis, daemon=True)
            protocol_thread.start()
            self.analysis_threads.append(protocol_thread)
    
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
                    
                    # Check for closed ports
                    closed_ports = known_ports - current_ports
                    if closed_ports:
                        self.log_message(f"🔒 Ports closed: {closed_ports}")
                    
                    known_ports = current_ports
                    self.protocol_analysis['open_ports'] = list(current_ports)
                
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
            
            # Try different protocols on the port
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
                self.learned_commands[f'http_port_{port}'] = {
                    'protocol': 'HTTP',
                    'port': port,
                    'response': result.stdout[:500],
                    'timestamp': datetime.now().isoformat()
                }
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
                    self.learned_commands[f'udp_port_{port}'] = {
                        'protocol': 'UDP',
                        'port': port,
                        'response': response.hex(),
                        'timestamp': datetime.now().isoformat()
                    }
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
                        self.learned_commands[f'tcp_port_{port}'] = {
                            'protocol': 'TCP',
                            'port': port,
                            'response': response.hex(),
                            'timestamp': datetime.now().isoformat()
                        }
                except socket.timeout:
                    continue
            
            sock.close()
        except Exception as e:
            pass
    
    def continuous_traffic_analysis(self):
        """Continuously analyze network traffic"""
        while self.running:
            try:
                if self.device_online:
                    self.analyze_traffic_patterns()
                time.sleep(10)  # Analyze every 10 seconds
            except Exception as e:
                self.log_message(f"Error in traffic analysis: {e}")
                time.sleep(30)
    
    def analyze_traffic_patterns(self):
        """Analyze network traffic for patterns"""
        try:
            # Use tcpdump to capture traffic
            cmd = [
                'tcpdump', '-i', 'any', '-n', '-c', '20',
                f'host {self.xiaomi_ip}', '-A', '-x'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                self.process_traffic_output(result.stdout)
        except Exception as e:
            self.log_message(f"Traffic analysis error: {e}")
    
    def process_traffic_output(self, output):
        """Process tcpdump output for patterns"""
        lines = output.split('\n')
        current_packet = []
        
        for line in lines:
            if 'IP' in line and self.xiaomi_ip in line:
                if current_packet:
                    self.analyze_packet(current_packet)
                current_packet = [line]
            elif current_packet:
                current_packet.append(line)
        
        if current_packet:
            self.analyze_packet(current_packet)
    
    def analyze_packet(self, packet_lines):
        """Analyze individual packet for command patterns"""
        packet_text = '\n'.join(packet_lines)
        
        # Look for JSON commands
        json_matches = re.findall(r'\{[^}]*\}', packet_text)
        for json_cmd in json_matches:
            try:
                cmd_data = json.loads(json_cmd)
                self.learn_command_from_json(cmd_data)
            except json.JSONDecodeError:
                continue
        
        # Look for HTTP commands
        if 'POST' in packet_text or 'GET' in packet_text:
            self.learn_http_command(packet_text)
        
        # Look for IR command patterns
        if 'ir' in packet_text.lower() or 'remote' in packet_text.lower():
            self.learn_ir_command(packet_text)
    
    def learn_command_from_json(self, cmd_data):
        """Learn from JSON command structure"""
        if 'method' in cmd_data:
            method = cmd_data['method']
            params = cmd_data.get('params', [])
            
            self.learned_commands[f'json_{method}'] = {
                'type': 'JSON',
                'method': method,
                'params': params,
                'timestamp': datetime.now().isoformat()
            }
            
            self.log_message(f"📝 Learned JSON command: {method} with params {params}")
    
    def learn_http_command(self, packet_text):
        """Learn from HTTP command"""
        if 'POST' in packet_text:
            self.learned_commands['http_post'] = {
                'type': 'HTTP_POST',
                'content': packet_text[:200],
                'timestamp': datetime.now().isoformat()
            }
            self.log_message("📝 Learned HTTP POST command")
        elif 'GET' in packet_text:
            self.learned_commands['http_get'] = {
                'type': 'HTTP_GET',
                'content': packet_text[:200],
                'timestamp': datetime.now().isoformat()
            }
            self.log_message("📝 Learned HTTP GET command")
    
    def learn_ir_command(self, packet_text):
        """Learn from IR command"""
        self.learned_commands['ir_command'] = {
            'type': 'IR',
            'content': packet_text[:200],
            'timestamp': datetime.now().isoformat()
        }
        self.log_message("📝 Learned IR command pattern")
    
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
    
    def continuous_protocol_analysis(self):
        """Continuously analyze protocol patterns"""
        while self.running:
            try:
                if self.device_online:
                    self.analyze_protocol_patterns()
                time.sleep(30)  # Analyze every 30 seconds
            except Exception as e:
                self.log_message(f"Error in protocol analysis: {e}")
                time.sleep(60)
    
    def analyze_protocol_patterns(self):
        """Analyze protocol patterns from learned data"""
        # Analyze response patterns
        if len(self.device_responses) > 0:
            self.analyze_response_patterns()
        
        # Analyze command sequences
        if len(self.command_sequences) > 0:
            self.analyze_command_sequences()
    
    def analyze_response_patterns(self):
        """Analyze patterns in device responses"""
        responses = list(self.device_responses)
        
        # Group by response type
        response_groups = defaultdict(list)
        for resp in responses:
            response_groups[resp['response'][:10]].append(resp)
        
        for pattern, group in response_groups.items():
            if len(group) > 1:
                self.log_message(f"🔄 Found response pattern: {pattern} ({len(group)} occurrences)")
    
    def analyze_command_sequences(self):
        """Analyze command sequences for patterns"""
        sequences = list(self.command_sequences)
        
        # Look for common command sequences
        if len(sequences) > 2:
            self.log_message(f"📊 Analyzing {len(sequences)} command sequences...")
    
    def save_learning_data(self):
        """Save all learning data to files"""
        try:
            # Save learned commands
            with open(self.commands_file, 'w') as f:
                json.dump(self.learned_commands, f, indent=2)
            
            # Save protocol analysis
            with open(self.protocol_file, 'w') as f:
                json.dump(self.protocol_analysis, f, indent=2)
            
            # Save learning summary
            learning_summary = {
                'total_commands_learned': len(self.learned_commands),
                'total_responses': len(self.device_responses),
                'device_online': self.device_online,
                'last_activity': self.last_activity.isoformat() if self.last_activity else None,
                'analysis_duration': str(datetime.now() - (self.last_activity or datetime.now())),
                'learned_commands': self.learned_commands,
                'protocol_analysis': self.protocol_analysis
            }
            
            with open(self.learning_file, 'w') as f:
                json.dump(learning_summary, f, indent=2)
            
            self.log_message("💾 Learning data saved successfully")
            
        except Exception as e:
            self.log_message(f"Error saving learning data: {e}")
    
    def run_continuous_analysis(self):
        """Run continuous analysis until stopped"""
        self.log_message("🚀 Starting Xiaomi Local Command Analyzer...")
        self.log_message(f"🎯 Target device: {self.xiaomi_ip}")
        self.log_message("📊 Analysis will run continuously until stopped")
        self.log_message("🛑 Press Ctrl+C to stop")
        
        self.running = True
        
        try:
            while self.running:
                # Check device connectivity
                self.check_device_connectivity()
                
                # Save learning data every 5 minutes
                if self.last_activity and (datetime.now() - self.last_activity).seconds > 300:
                    self.save_learning_data()
                    self.last_activity = datetime.now()
                
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            self.log_message("🛑 Analysis stopped by user")
        except Exception as e:
            self.log_message(f"❌ Analysis error: {e}")
        finally:
            self.running = False
            self.save_learning_data()
            self.log_message("✅ Analysis completed and data saved")

def main():
    """Main function"""
    analyzer = XiaomiLocalAnalyzer()
    analyzer.run_continuous_analysis()

if __name__ == "__main__":
    main()
