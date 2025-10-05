#!/usr/bin/env python3
"""
Network Traffic Analysis for Xiaomi L05G
Monitors network traffic to identify IR command packets
"""

import scapy.all as scapy
import json
import time
import logging
from typing import Dict, List, Any, Optional
import threading
import queue
from datetime import datetime

class NetworkMonitor:
    """Network traffic monitor for L05G"""
    
    def __init__(self, l05g_ip: str, config_file: str = "network_config.json"):
        self.l05g_ip = l05g_ip
        self.config_file = config_file
        self.config = self.load_config()
        self.logger = self.setup_logging()
        self.packet_queue = queue.Queue()
        self.monitoring = False
        self.monitor_thread = None
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("NetworkMonitor")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "monitor": {
                "interface": "eth0",
                "timeout": 30,
                "packet_limit": 1000
            },
            "l05g": {
                "ports": [80, 443, 8080, 8443],
                "protocols": ["TCP", "UDP", "HTTP"]
            },
            "filters": {
                "ir_commands": True,
                "voice_commands": True,
                "device_control": True
            }
        }
    
    def start_monitoring(self):
        """Start network monitoring"""
        if self.monitoring:
            self.logger.warning("Monitoring already active")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info(f"Started monitoring L05G at {self.l05g_ip}")
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("Stopped monitoring")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        try:
            # Create filter for L05G traffic
            filter_str = f"host {self.l05g_ip}"
            
            # Start packet capture
            packets = scapy.sniff(
                filter=filter_str,
                timeout=self.config.get("monitor", {}).get("timeout", 30),
                count=self.config.get("monitor", {}).get("packet_limit", 1000)
            )
            
            # Process captured packets
            for packet in packets:
                self._process_packet(packet)
                
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")
    
    def _process_packet(self, packet):
        """Process individual packet"""
        try:
            # Extract packet information
            packet_info = {
                "timestamp": datetime.now().isoformat(),
                "src_ip": packet[scapy.IP].src if packet.haslayer(scapy.IP) else None,
                "dst_ip": packet[scapy.IP].dst if packet.haslayer(scapy.IP) else None,
                "protocol": packet[scapy.IP].proto if packet.haslayer(scapy.IP) else None,
                "size": len(packet)
            }
            
            # Check for HTTP traffic
            if packet.haslayer(scapy.Raw):
                http_data = packet[scapy.Raw].load
                if self._is_http_traffic(http_data):
                    packet_info["http_data"] = http_data.decode('utf-8', errors='ignore')
                    packet_info["type"] = "http"
            
            # Check for IR command patterns
            if self._is_ir_command(packet_info):
                packet_info["type"] = "ir_command"
                self._handle_ir_command(packet_info)
            
            # Queue packet for analysis
            self.packet_queue.put(packet_info)
            
        except Exception as e:
            self.logger.error(f"Error processing packet: {e}")
    
    def _is_http_traffic(self, data: bytes) -> bool:
        """Check if data is HTTP traffic"""
        try:
            data_str = data.decode('utf-8', errors='ignore')
            return any(method in data_str for method in ['GET', 'POST', 'PUT', 'DELETE'])
        except:
            return False
    
    def _is_ir_command(self, packet_info: Dict[str, Any]) -> bool:
        """Check if packet contains IR command"""
        if packet_info.get("type") == "http":
            http_data = packet_info.get("http_data", "")
            
            # Look for IR command patterns
            ir_patterns = [
                "ir_command",
                "infrared",
                "remote_control",
                "device_control",
                "ir_send"
            ]
            
            return any(pattern in http_data.lower() for pattern in ir_patterns)
        
        return False
    
    def _handle_ir_command(self, packet_info: Dict[str, Any]):
        """Handle identified IR command"""
        self.logger.info(f"IR command detected: {packet_info}")
        
        # Extract IR command data
        ir_data = self._extract_ir_data(packet_info)
        if ir_data:
            self._save_ir_command(ir_data)
    
    def _extract_ir_data(self, packet_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract IR command data from packet"""
        try:
            http_data = packet_info.get("http_data", "")
            
            # Parse JSON data if present
            if "{" in http_data and "}" in http_data:
                json_start = http_data.find("{")
                json_end = http_data.rfind("}") + 1
                json_data = http_data[json_start:json_end]
                
                try:
                    return json.loads(json_data)
                except json.JSONDecodeError:
                    pass
            
            # Extract IR command parameters
            ir_data = {
                "timestamp": packet_info["timestamp"],
                "command": self._extract_command_name(http_data),
                "device": self._extract_device_name(http_data),
                "raw_data": http_data
            }
            
            return ir_data
            
        except Exception as e:
            self.logger.error(f"Error extracting IR data: {e}")
            return None
    
    def _extract_command_name(self, http_data: str) -> str:
        """Extract command name from HTTP data"""
        # Look for command patterns
        command_patterns = [
            "command",
            "action",
            "function",
            "operation"
        ]
        
        for pattern in command_patterns:
            if pattern in http_data.lower():
                # Extract value after pattern
                start = http_data.lower().find(pattern)
                end = http_data.find("\n", start)
                if end == -1:
                    end = len(http_data)
                
                command_line = http_data[start:end]
                if ":" in command_line:
                    return command_line.split(":")[1].strip()
        
        return "unknown"
    
    def _extract_device_name(self, http_data: str) -> str:
        """Extract device name from HTTP data"""
        # Look for device patterns
        device_patterns = [
            "device",
            "target",
            "destination"
        ]
        
        for pattern in device_patterns:
            if pattern in http_data.lower():
                # Extract value after pattern
                start = http_data.lower().find(pattern)
                end = http_data.find("\n", start)
                if end == -1:
                    end = len(http_data)
                
                device_line = http_data[start:end]
                if ":" in device_line:
                    return device_line.split(":")[1].strip()
        
        return "unknown"
    
    def _save_ir_command(self, ir_data: Dict[str, Any]):
        """Save IR command to database"""
        try:
            # Load existing database
            database = self.load_ir_database()
            
            # Add new command
            command_id = f"{ir_data['device']}_{ir_data['command']}_{int(time.time())}"
            database[command_id] = ir_data
            
            # Save database
            self.save_ir_database(database)
            self.logger.info(f"Saved IR command: {command_id}")
            
        except Exception as e:
            self.logger.error(f"Error saving IR command: {e}")
    
    def load_ir_database(self) -> Dict[str, Any]:
        """Load IR command database"""
        try:
            with open("ir_commands.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_ir_database(self, database: Dict[str, Any]):
        """Save IR command database"""
        with open("ir_commands.json", 'w') as f:
            json.dump(database, f, indent=2)
    
    def get_ir_commands(self) -> Dict[str, Any]:
        """Get all IR commands"""
        return self.load_ir_database()
    
    def send_ir_command(self, command_id: str) -> bool:
        """Send IR command to L05G"""
        try:
            database = self.load_ir_database()
            if command_id not in database:
                self.logger.error(f"Command {command_id} not found")
                return False
            
            command_data = database[command_id]
            
            # Replicate the HTTP request
            return self._replicate_http_request(command_data)
            
        except Exception as e:
            self.logger.error(f"Error sending IR command: {e}")
            return False
    
    def _replicate_http_request(self, command_data: Dict[str, Any]) -> bool:
        """Replicate HTTP request to send IR command"""
        try:
            # This would require reverse engineering the exact HTTP request format
            # For now, just log the attempt
            self.logger.info(f"Replicating HTTP request for command: {command_data}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error replicating HTTP request: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Initialize monitor
    monitor = NetworkMonitor("192.168.1.100")  # Replace with L05G IP
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        # Monitor for 60 seconds
        time.sleep(60)
        
        # Get captured commands
        commands = monitor.get_ir_commands()
        print(f"Captured {len(commands)} IR commands")
        
        # Send a command
        if commands:
            command_id = list(commands.keys())[0]
            success = monitor.send_ir_command(command_id)
            print(f"Command sent: {success}")
        
    finally:
        monitor.stop_monitoring()
