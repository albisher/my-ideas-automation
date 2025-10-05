#!/usr/bin/env python3
"""
Xiaomi Command Analyzer
Monitors and analyzes communication patterns with Xiaomi device at 192.168.68.68
Learns command structures and protocols for sending commands
"""

import subprocess
import json
import time
import re
from datetime import datetime
import os
import socket
import struct
import threading
from collections import defaultdict

# Configuration
XIAOMI_IP = "192.168.68.68"
XIAOMI_PORT = 54321  # Default Xiaomi port
LOG_FILE = "/config/xiaomi_analysis.log"
COMMANDS_FILE = "/config/xiaomi_commands.json"
PROTOCOL_FILE = "/config/xiaomi_protocol.json"

class XiaomiCommandAnalyzer:
    def __init__(self):
        self.xiaomi_ip = XIAOMI_IP
        self.xiaomi_port = XIAOMI_PORT
        self.log_file = LOG_FILE
        self.commands_file = COMMANDS_FILE
        self.protocol_file = PROTOCOL_FILE
        self.discovered_commands = {}
        self.protocol_info = {}
        self.packet_analysis = defaultdict(list)
        self.running = False
        
    def log_message(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
    
    def check_xiaomi_connectivity(self):
        """Check if Xiaomi device is reachable"""
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '1', self.xiaomi_ip], 
                                  capture_output=True, text=True)
            return "1 received" in result.stdout
        except Exception as e:
            self.log_message(f"Error checking connectivity: {e}")
            return False
    
    def scan_xiaomi_ports(self):
        """Scan common Xiaomi ports to find open services"""
        common_ports = [54321, 8080, 80, 443, 22, 23, 554, 8554]
        open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.xiaomi_ip, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
                    self.log_message(f"Port {port} is open")
            except Exception as e:
                self.log_message(f"Error scanning port {port}: {e}")
        
        return open_ports
    
    def analyze_xiaomi_protocol(self):
        """Analyze Xiaomi device protocol and communication patterns"""
        self.log_message("Starting Xiaomi protocol analysis...")
        
        # Check connectivity
        if not self.check_xiaomi_connectivity():
            self.log_message(f"Warning: Xiaomi device at {self.xiaomi_ip} is not reachable")
            return False
        
        # Scan for open ports
        open_ports = self.scan_xiaomi_ports()
        self.protocol_info['open_ports'] = open_ports
        self.log_message(f"Open ports: {open_ports}")
        
        # Try to identify device type and capabilities
        device_info = self.identify_device_type()
        self.protocol_info['device_info'] = device_info
        
        # Analyze network traffic patterns
        self.analyze_traffic_patterns()
        
        return True
    
    def identify_device_type(self):
        """Try to identify the type of Xiaomi device"""
        device_info = {
            'type': 'unknown',
            'capabilities': [],
            'protocols': []
        }
        
        # Check for common Xiaomi device signatures
        try:
            # Try HTTP requests to common endpoints
            http_endpoints = ['/', '/status', '/info', '/api/status']
            for endpoint in http_endpoints:
                try:
                    result = subprocess.run([
                        'curl', '-s', '-m', '5', 
                        f'http://{self.xiaomi_ip}{endpoint}'
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0 and result.stdout:
                        self.log_message(f"HTTP response from {endpoint}: {result.stdout[:200]}")
                        device_info['protocols'].append('HTTP')
                        
                        # Check for Xiaomi-specific responses
                        if 'xiaomi' in result.stdout.lower() or 'miio' in result.stdout.lower():
                            device_info['type'] = 'xiaomi_ir_remote'
                            device_info['capabilities'].append('ir_control')
                except Exception as e:
                    continue
            
            # Try UDP discovery (common for Xiaomi devices)
            try:
                self.send_udp_discovery()
                device_info['protocols'].append('UDP')
            except Exception as e:
                self.log_message(f"UDP discovery failed: {e}")
            
        except Exception as e:
            self.log_message(f"Error identifying device: {e}")
        
        return device_info
    
    def send_udp_discovery(self):
        """Send UDP discovery packets to Xiaomi device"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            
            # Common Xiaomi discovery packets
            discovery_packets = [
                b'\x21\x31\x00\x20\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff',
                b'{"id":1,"method":"miIO.info","params":[]}',
                b'{"method":"get_prop","params":["power","mode","temp"]}'
            ]
            
            for packet in discovery_packets:
                sock.sendto(packet, (self.xiaomi_ip, self.xiaomi_port))
                time.sleep(0.5)
                
                try:
                    response, addr = sock.recvfrom(1024)
                    self.log_message(f"UDP response from {addr}: {response.hex()}")
                    self.protocol_info['udp_response'] = response.hex()
                except socket.timeout:
                    continue
            
            sock.close()
            
        except Exception as e:
            self.log_message(f"UDP discovery error: {e}")
    
    def analyze_traffic_patterns(self):
        """Analyze network traffic to understand communication patterns"""
        self.log_message("Analyzing traffic patterns...")
        
        # Monitor traffic for a short period
        try:
            cmd = [
                'tcpdump', '-i', 'any', '-n', '-c', '50',
                f'host {self.xiaomi_ip}', '-A'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.analyze_tcpdump_output(result.stdout)
            else:
                self.log_message("tcpdump analysis failed")
                
        except Exception as e:
            self.log_message(f"Traffic analysis error: {e}")
    
    def analyze_tcpdump_output(self, output):
        """Analyze tcpdump output for command patterns"""
        lines = output.split('\n')
        protocols = set()
        commands = []
        
        for line in lines:
            # Look for protocol indicators
            if 'TCP' in line:
                protocols.add('TCP')
            elif 'UDP' in line:
                protocols.add('UDP')
            elif 'HTTP' in line:
                protocols.add('HTTP')
            
            # Look for command-like patterns
            if 'POST' in line or 'GET' in line:
                commands.append(line.strip())
            elif '{"' in line or 'command' in line.lower():
                commands.append(line.strip())
        
        self.protocol_info['detected_protocols'] = list(protocols)
        self.protocol_info['potential_commands'] = commands[:10]  # Keep first 10
        
        self.log_message(f"Detected protocols: {list(protocols)}")
        self.log_message(f"Potential commands: {len(commands)}")
    
    def generate_command_templates(self):
        """Generate command templates based on analysis"""
        templates = {
            'ir_commands': {
                'power': '{"method":"set_power","params":["on"]}',
                'volume_up': '{"method":"set_volume","params":["up"]}',
                'volume_down': '{"method":"set_volume","params":["down"]}',
                'channel_up': '{"method":"set_channel","params":["up"]}',
                'channel_down': '{"method":"set_channel","params":["down"]}',
                'mute': '{"method":"set_mute","params":["on"]}'
            },
            'http_commands': {
                'power': 'POST /api/ir/power',
                'volume_up': 'POST /api/ir/volume_up',
                'volume_down': 'POST /api/ir/volume_down',
                'channel_up': 'POST /api/ir/channel_up',
                'channel_down': 'POST /api/ir/channel_down'
            },
            'udp_commands': {
                'discovery': '{"id":1,"method":"miIO.info","params":[]}',
                'get_status': '{"method":"get_prop","params":["power","mode"]}',
                'send_ir': '{"method":"send_ir","params":["power_code"]}'
            }
        }
        
        self.discovered_commands = templates
        return templates
    
    def test_command_sending(self):
        """Test sending commands to Xiaomi device"""
        self.log_message("Testing command sending...")
        
        test_commands = [
            ('UDP', '{"method":"miIO.info","params":[]}'),
            ('HTTP', 'GET /api/status'),
            ('HTTP', 'POST /api/ir/power')
        ]
        
        results = {}
        
        for protocol, command in test_commands:
            try:
                if protocol == 'UDP':
                    result = self.send_udp_command(command)
                elif protocol == 'HTTP':
                    result = self.send_http_command(command)
                
                results[protocol] = result
                self.log_message(f"{protocol} command result: {result}")
                
            except Exception as e:
                self.log_message(f"Error testing {protocol} command: {e}")
                results[protocol] = f"Error: {e}"
        
        return results
    
    def send_udp_command(self, command):
        """Send UDP command to Xiaomi device"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            
            if isinstance(command, str):
                command = command.encode()
            
            sock.sendto(command, (self.xiaomi_ip, self.xiaomi_port))
            
            try:
                response, addr = sock.recvfrom(1024)
                sock.close()
                return f"Response from {addr}: {response.hex()}"
            except socket.timeout:
                sock.close()
                return "No response (timeout)"
                
        except Exception as e:
            return f"UDP error: {e}"
    
    def send_http_command(self, command):
        """Send HTTP command to Xiaomi device"""
        try:
            if command.startswith('GET'):
                url = f"http://{self.xiaomi_ip}{command.split()[1]}"
                result = subprocess.run(['curl', '-s', '-m', '5', url], 
                                      capture_output=True, text=True)
            elif command.startswith('POST'):
                url = f"http://{self.xiaomi_ip}{command.split()[1]}"
                result = subprocess.run(['curl', '-s', '-m', '5', '-X', 'POST', url], 
                                      capture_output=True, text=True)
            else:
                return "Invalid HTTP command format"
            
            if result.returncode == 0:
                return f"HTTP response: {result.stdout[:200]}"
            else:
                return f"HTTP error: {result.stderr}"
                
        except Exception as e:
            return f"HTTP error: {e}"
    
    def save_analysis_results(self):
        """Save analysis results to files"""
        try:
            # Save protocol information
            with open(self.protocol_file, 'w') as f:
                json.dump(self.protocol_info, f, indent=2)
            
            # Save discovered commands
            with open(self.commands_file, 'w') as f:
                json.dump(self.discovered_commands, f, indent=2)
            
            self.log_message("Analysis results saved successfully")
            
        except Exception as e:
            self.log_message(f"Error saving results: {e}")
    
    def run_analysis(self):
        """Run complete analysis of Xiaomi device"""
        self.log_message("Starting Xiaomi Command Analyzer...")
        self.log_message(f"Target device: {self.xiaomi_ip}")
        
        # Initialize files
        with open(self.log_file, 'w') as f:
            f.write(f"Xiaomi Command Analysis started at {datetime.now()}\n")
        
        # Run analysis steps
        if self.analyze_xiaomi_protocol():
            self.log_message("Protocol analysis completed")
            
            # Generate command templates
            self.generate_command_templates()
            self.log_message("Command templates generated")
            
            # Test command sending
            test_results = self.test_command_sending()
            self.protocol_info['test_results'] = test_results
            
            # Save results
            self.save_analysis_results()
            
            self.log_message("Analysis completed successfully")
            return True
        else:
            self.log_message("Analysis failed - device not reachable")
            return False

def main():
    """Main function"""
    analyzer = XiaomiCommandAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        print("✅ Xiaomi Command Analysis completed successfully")
        print(f"📁 Results saved to:")
        print(f"   - Protocol: {analyzer.protocol_file}")
        print(f"   - Commands: {analyzer.commands_file}")
        print(f"   - Log: {analyzer.log_file}")
    else:
        print("❌ Xiaomi Command Analysis failed")
        print("Check if the device is reachable and try again")

if __name__ == "__main__":
    main()
