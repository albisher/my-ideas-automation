#!/usr/bin/env python3
"""
L05G Network Traffic Analyzer
Advanced network analysis for Xiaomi L05G Google Voice integration
"""

import scapy.all as scapy
import json
import time
import logging
import threading
import queue
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
import base64

class L05GNetworkAnalyzer:
    """Advanced network analyzer for L05G Google Voice integration"""
    
    def __init__(self, l05g_ip: str, config_file: str = "l05g_config.json"):
        self.l05g_ip = l05g_ip
        self.config_file = config_file
        self.config = self.load_config()
        self.logger = self.setup_logging()
        
        # Network analysis components
        self.packet_queue = queue.Queue()
        self.command_database = {}
        self.voice_patterns = self.load_voice_patterns()
        self.ir_patterns = self.load_ir_patterns()
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        # Google Assistant integration
        self.assistant_commands = {}
        self.chromecast_commands = {}
        self.xiaomi_commands = {}
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("L05GNetworkAnalyzer")
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
                "packet_limit": 1000,
                "capture_duration": 60
            },
            "l05g": {
                "ip": self.l05g_ip,
                "ports": [80, 443, 8080, 8443, 8008, 8009],
                "protocols": ["TCP", "UDP", "HTTP", "HTTPS", "mDNS"]
            },
            "google_assistant": {
                "api_endpoints": [
                    "assistant.googleapis.com",
                    "assistant.google.com",
                    "www.googleapis.com"
                ],
                "voice_patterns": True,
                "command_analysis": True
            },
            "chromecast": {
                "enabled": True,
                "ports": [8008, 8009],
                "protocols": ["mDNS", "HTTP"]
            },
            "xiaomi_home": {
                "enabled": True,
                "api_endpoints": [
                    "api.io.mi.com",
                    "api.io.mi.com",
                    "api.io.mi.com"
                ]
            }
        }
    
    def load_voice_patterns(self) -> Dict[str, List[str]]:
        """Load voice command patterns"""
        return {
            "device_control": [
                "turn on", "turn off", "switch on", "switch off",
                "power on", "power off", "start", "stop"
            ],
            "volume_control": [
                "volume up", "volume down", "louder", "quieter",
                "increase volume", "decrease volume", "mute", "unmute"
            ],
            "temperature_control": [
                "temperature up", "temperature down", "hotter", "colder",
                "increase temperature", "decrease temperature"
            ],
            "channel_control": [
                "next channel", "previous channel", "channel up", "channel down"
            ]
        }
    
    def load_ir_patterns(self) -> List[str]:
        """Load IR command patterns"""
        return [
            "ir_command", "infrared", "remote_control", "device_control",
            "ir_send", "ir_transmit", "ir_signal", "ir_code"
        ]
    
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
            # Create comprehensive filter for L05G traffic
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
                "size": len(packet),
                "raw_data": None
            }
            
            # Analyze packet content
            if packet.haslayer(scapy.Raw):
                raw_data = packet[scapy.Raw].load
                packet_info["raw_data"] = raw_data
                
                # Check for Google Assistant traffic
                if self._is_google_assistant_traffic(packet_info):
                    self._analyze_google_assistant_traffic(packet_info)
                
                # Check for Chromecast traffic
                if self._is_chromecast_traffic(packet_info):
                    self._analyze_chromecast_traffic(packet_info)
                
                # Check for Xiaomi Home traffic
                if self._is_xiaomi_traffic(packet_info):
                    self._analyze_xiaomi_traffic(packet_info)
                
                # Check for IR commands
                if self._is_ir_command(packet_info):
                    self._handle_ir_command(packet_info)
            
            # Queue packet for analysis
            self.packet_queue.put(packet_info)
            
        except Exception as e:
            self.logger.error(f"Error processing packet: {e}")
    
    def _is_google_assistant_traffic(self, packet_info: Dict[str, Any]) -> bool:
        """Check if packet is Google Assistant traffic"""
        if not packet_info.get("raw_data"):
            return False
        
        try:
            data_str = packet_info["raw_data"].decode('utf-8', errors='ignore')
            
            # Check for Google Assistant endpoints
            google_endpoints = self.config.get("google_assistant", {}).get("api_endpoints", [])
            for endpoint in google_endpoints:
                if endpoint in data_str:
                    return True
            
            # Check for Google Assistant patterns
            google_patterns = [
                "assistant", "google", "voice", "speech",
                "recognition", "command", "action"
            ]
            
            return any(pattern in data_str.lower() for pattern in google_patterns)
            
        except:
            return False
    
    def _is_chromecast_traffic(self, packet_info: Dict[str, Any]) -> bool:
        """Check if packet is Chromecast traffic"""
        if not packet_info.get("raw_data"):
            return False
        
        try:
            data_str = packet_info["raw_data"].decode('utf-8', errors='ignore')
            
            # Check for Chromecast patterns
            chromecast_patterns = [
                "chromecast", "cast", "media", "playback",
                "mDNS", "discovery", "device"
            ]
            
            return any(pattern in data_str.lower() for pattern in chromecast_patterns)
            
        except:
            return False
    
    def _is_xiaomi_traffic(self, packet_info: Dict[str, Any]) -> bool:
        """Check if packet is Xiaomi Home traffic"""
        if not packet_info.get("raw_data"):
            return False
        
        try:
            data_str = packet_info["raw_data"].decode('utf-8', errors='ignore')
            
            # Check for Xiaomi endpoints
            xiaomi_endpoints = self.config.get("xiaomi_home", {}).get("api_endpoints", [])
            for endpoint in xiaomi_endpoints:
                if endpoint in data_str:
                    return True
            
            # Check for Xiaomi patterns
            xiaomi_patterns = [
                "xiaomi", "mi home", "miio", "device",
                "ir", "infrared", "remote"
            ]
            
            return any(pattern in data_str.lower() for pattern in xiaomi_patterns)
            
        except:
            return False
    
    def _is_ir_command(self, packet_info: Dict[str, Any]) -> bool:
        """Check if packet contains IR command"""
        if not packet_info.get("raw_data"):
            return False
        
        try:
            data_str = packet_info["raw_data"].decode('utf-8', errors='ignore')
            
            # Check for IR command patterns
            return any(pattern in data_str.lower() for pattern in self.ir_patterns)
            
        except:
            return False
    
    def _analyze_google_assistant_traffic(self, packet_info: Dict[str, Any]):
        """Analyze Google Assistant traffic"""
        self.logger.info("Google Assistant traffic detected")
        
        # Extract voice command
        voice_command = self._extract_voice_command(packet_info)
        if voice_command:
            self._handle_voice_command(voice_command)
    
    def _analyze_chromecast_traffic(self, packet_info: Dict[str, Any]):
        """Analyze Chromecast traffic"""
        self.logger.info("Chromecast traffic detected")
        
        # Extract media command
        media_command = self._extract_media_command(packet_info)
        if media_command:
            self._handle_media_command(media_command)
    
    def _analyze_xiaomi_traffic(self, packet_info: Dict[str, Any]):
        """Analyze Xiaomi Home traffic"""
        self.logger.info("Xiaomi Home traffic detected")
        
        # Extract device command
        device_command = self._extract_device_command(packet_info)
        if device_command:
            self._handle_device_command(device_command)
    
    def _extract_voice_command(self, packet_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract voice command from packet"""
        try:
            data_str = packet_info["raw_data"].decode('utf-8', errors='ignore')
            
            # Look for voice command patterns
            for category, patterns in self.voice_patterns.items():
                for pattern in patterns:
                    if pattern in data_str.lower():
                        return {
                            "type": "voice_command",
                            "category": category,
                            "pattern": pattern,
                            "data": data_str,
                            "timestamp": packet_info["timestamp"]
                        }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting voice command: {e}")
            return None
    
    def _extract_media_command(self, packet_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract media command from packet"""
        try:
            data_str = packet_info["raw_data"].decode('utf-8', errors='ignore')
            
            # Look for media command patterns
            media_patterns = [
                "play", "pause", "stop", "next", "previous",
                "volume", "mute", "unmute", "seek"
            ]
            
            for pattern in media_patterns:
                if pattern in data_str.lower():
                    return {
                        "type": "media_command",
                        "command": pattern,
                        "data": data_str,
                        "timestamp": packet_info["timestamp"]
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting media command: {e}")
            return None
    
    def _extract_device_command(self, packet_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract device command from packet"""
        try:
            data_str = packet_info["raw_data"].decode('utf-8', errors='ignore')
            
            # Look for device command patterns
            device_patterns = [
                "device", "control", "command", "action",
                "ir", "infrared", "remote"
            ]
            
            for pattern in device_patterns:
                if pattern in data_str.lower():
                    return {
                        "type": "device_command",
                        "command": pattern,
                        "data": data_str,
                        "timestamp": packet_info["timestamp"]
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting device command: {e}")
            return None
    
    def _handle_voice_command(self, voice_command: Dict[str, Any]):
        """Handle detected voice command"""
        self.logger.info(f"Voice command detected: {voice_command['pattern']}")
        
        # Store command in database
        command_id = f"voice_{int(time.time())}"
        self.command_database[command_id] = voice_command
        
        # Analyze for IR command generation
        ir_command = self._analyze_voice_for_ir(voice_command)
        if ir_command:
            self._handle_ir_command(ir_command)
    
    def _handle_media_command(self, media_command: Dict[str, Any]):
        """Handle detected media command"""
        self.logger.info(f"Media command detected: {media_command['command']}")
        
        # Store command in database
        command_id = f"media_{int(time.time())}"
        self.command_database[command_id] = media_command
    
    def _handle_device_command(self, device_command: Dict[str, Any]):
        """Handle detected device command"""
        self.logger.info(f"Device command detected: {device_command['command']}")
        
        # Store command in database
        command_id = f"device_{int(time.time())}"
        self.command_database[command_id] = device_command
    
    def _analyze_voice_for_ir(self, voice_command: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze voice command for IR command generation"""
        try:
            # Look for IR command patterns in voice command
            if "ir" in voice_command["data"].lower():
                return {
                    "type": "ir_command",
                    "source": "voice",
                    "command": voice_command["pattern"],
                    "data": voice_command["data"],
                    "timestamp": voice_command["timestamp"]
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing voice for IR: {e}")
            return None
    
    def _handle_ir_command(self, ir_command: Dict[str, Any]):
        """Handle detected IR command"""
        self.logger.info(f"IR command detected: {ir_command}")
        
        # Store IR command in database
        command_id = f"ir_{int(time.time())}"
        self.command_database[command_id] = ir_command
        
        # Save to file
        self.save_command_database()
    
    def save_command_database(self):
        """Save command database to file"""
        try:
            with open("l05g_commands.json", 'w') as f:
                json.dump(self.command_database, f, indent=2)
            self.logger.info("Command database saved")
        except Exception as e:
            self.logger.error(f"Error saving command database: {e}")
    
    def load_command_database(self) -> Dict[str, Any]:
        """Load command database from file"""
        try:
            with open("l05g_commands.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get_commands(self) -> Dict[str, Any]:
        """Get all captured commands"""
        return self.command_database
    
    def get_ir_commands(self) -> Dict[str, Any]:
        """Get IR commands only"""
        ir_commands = {}
        for command_id, command_data in self.command_database.items():
            if command_data.get("type") == "ir_command":
                ir_commands[command_id] = command_data
        return ir_commands
    
    def get_voice_commands(self) -> Dict[str, Any]:
        """Get voice commands only"""
        voice_commands = {}
        for command_id, command_data in self.command_database.items():
            if command_data.get("type") == "voice_command":
                voice_commands[command_id] = command_data
        return voice_commands

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = L05GNetworkAnalyzer("192.168.1.100")  # Replace with L05G IP
    
    # Start monitoring
    analyzer.start_monitoring()
    
    try:
        # Monitor for 60 seconds
        time.sleep(60)
        
        # Get captured commands
        commands = analyzer.get_commands()
        print(f"Captured {len(commands)} commands")
        
        # Get IR commands
        ir_commands = analyzer.get_ir_commands()
        print(f"Captured {len(ir_commands)} IR commands")
        
        # Get voice commands
        voice_commands = analyzer.get_voice_commands()
        print(f"Captured {len(voice_commands)} voice commands")
        
    finally:
        analyzer.stop_monitoring()
