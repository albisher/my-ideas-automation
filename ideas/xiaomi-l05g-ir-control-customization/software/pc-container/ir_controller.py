#!/usr/bin/env python3
"""
IR Controller for PC Container
Supports multiple IR control methods including BroadLink RM4 Pro
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time

try:
    import broadlink
    BROADLINK_AVAILABLE = True
except ImportError:
    BROADLINK_AVAILABLE = False
    print("Warning: broadlink not available. Install with: pip install broadlink")

try:
    import lirc
    LIRC_AVAILABLE = True
except ImportError:
    LIRC_AVAILABLE = False
    print("Warning: lirc not available. Install with: pip install python-lirc")

class IRProtocol(Enum):
    """Supported IR protocols"""
    NEC = "nec"
    RC5 = "rc5"
    RC6 = "rc6"
    SONY = "sony"
    RAW = "raw"

@dataclass
class IRCommand:
    """IR command data structure"""
    name: str
    protocol: IRProtocol
    data: List[int]
    device: str
    description: str = ""

class IRController:
    """Main IR controller class supporting multiple backends"""
    
    def __init__(self, config_file: str = "ir_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.devices = {}
        self.commands = {}
        self.logger = self.setup_logging()
        
        # Initialize available backends
        self.broadlink_device = None
        self.lirc_client = None
        
        self.initialize_backends()
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("IRController")
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
            self.logger.warning(f"Config file {self.config_file} not found, using defaults")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "broadlink": {
                "enabled": True,
                "timeout": 5,
                "retry_count": 3
            },
            "lirc": {
                "enabled": False,
                "config_file": "/etc/lirc/lircd.conf"
            },
            "devices": {},
            "commands": {}
        }
    
    def initialize_backends(self):
        """Initialize available IR backends"""
        # Initialize BroadLink
        if self.config.get("broadlink", {}).get("enabled", True) and BROADLINK_AVAILABLE:
            self.initialize_broadlink()
        
        # Initialize LIRC
        if self.config.get("lirc", {}).get("enabled", False) and LIRC_AVAILABLE:
            self.initialize_lirc()
    
    def initialize_broadlink(self):
        """Initialize BroadLink device"""
        try:
            self.logger.info("Discovering BroadLink devices...")
            devices = broadlink.discover(timeout=self.config.get("broadlink", {}).get("timeout", 5))
            
            if devices:
                self.broadlink_device = devices[0]
                self.broadlink_device.auth()
                self.logger.info(f"Connected to BroadLink device: {self.broadlink_device}")
            else:
                self.logger.warning("No BroadLink devices found")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize BroadLink: {e}")
    
    def initialize_lirc(self):
        """Initialize LIRC client"""
        try:
            self.lirc_client = lirc.Client()
            self.logger.info("LIRC client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize LIRC: {e}")
    
    def add_command(self, command: IRCommand):
        """Add IR command to database"""
        self.commands[command.name] = command
        self.logger.info(f"Added command: {command.name}")
    
    def send_command(self, command_name: str, device_name: str = None) -> bool:
        """Send IR command by name"""
        if command_name not in self.commands:
            self.logger.error(f"Command '{command_name}' not found")
            return False
        
        command = self.commands[command_name]
        
        # Try BroadLink first
        if self.broadlink_device:
            return self.send_broadlink_command(command)
        
        # Try LIRC
        if self.lirc_client:
            return self.send_lirc_command(command)
        
        self.logger.error("No IR backend available")
        return False
    
    def send_broadlink_command(self, command: IRCommand) -> bool:
        """Send command via BroadLink"""
        try:
            if command.protocol == IRProtocol.RAW:
                # Convert raw data to BroadLink format
                data = bytes(command.data)
            else:
                # Use protocol-specific encoding
                data = self.encode_ir_data(command)
            
            self.broadlink_device.send_data(data)
            self.logger.info(f"Sent BroadLink command: {command.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send BroadLink command: {e}")
            return False
    
    def send_lirc_command(self, command: IRCommand) -> bool:
        """Send command via LIRC"""
        try:
            self.lirc_client.send_once(command.device, command.name)
            self.logger.info(f"Sent LIRC command: {command.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send LIRC command: {e}")
            return False
    
    def encode_ir_data(self, command: IRCommand) -> bytes:
        """Encode IR data based on protocol"""
        if command.protocol == IRProtocol.NEC:
            return self.encode_nec(command.data)
        elif command.protocol == IRProtocol.RC5:
            return self.encode_rc5(command.data)
        elif command.protocol == IRProtocol.RAW:
            return bytes(command.data)
        else:
            return bytes(command.data)
    
    def encode_nec(self, data: List[int]) -> bytes:
        """Encode NEC protocol data"""
        # Simplified NEC encoding - in practice, use proper IR library
        return bytes(data)
    
    def encode_rc5(self, data: List[int]) -> bytes:
        """Encode RC5 protocol data"""
        # Simplified RC5 encoding - in practice, use proper IR library
        return bytes(data)
    
    def learn_command(self, command_name: str, device_name: str) -> bool:
        """Learn IR command from remote"""
        if not self.broadlink_device:
            self.logger.error("BroadLink device not available for learning")
            return False
        
        try:
            self.logger.info(f"Learning command '{command_name}' for device '{device_name}'")
            self.logger.info("Press the button on your remote now...")
            
            # Start learning mode
            self.broadlink_device.enter_learning()
            
            # Wait for user to press button
            time.sleep(10)  # Give user time to press button
            
            # Get learned data
            data = self.broadlink_device.check_data()
            if data:
                # Create new command
                command = IRCommand(
                    name=command_name,
                    protocol=IRProtocol.RAW,
                    data=list(data),
                    device=device_name,
                    description=f"Learned command for {device_name}"
                )
                
                self.add_command(command)
                self.save_commands()
                self.logger.info(f"Successfully learned command: {command_name}")
                return True
            else:
                self.logger.error("No data received during learning")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to learn command: {e}")
            return False
    
    def save_commands(self):
        """Save commands to configuration file"""
        commands_data = {}
        for name, command in self.commands.items():
            commands_data[name] = {
                "protocol": command.protocol.value,
                "data": command.data,
                "device": command.device,
                "description": command.description
            }
        
        self.config["commands"] = commands_data
        
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def list_commands(self) -> List[str]:
        """List available commands"""
        return list(self.commands.keys())
    
    def get_device_commands(self, device_name: str) -> List[str]:
        """Get commands for specific device"""
        return [name for name, cmd in self.commands.items() 
                if cmd.device == device_name]

# Example usage and testing
if __name__ == "__main__":
    controller = IRController()
    
    # Example: Add a TV power command
    tv_power = IRCommand(
        name="tv_power",
        protocol=IRProtocol.NEC,
        data=[0x20, 0xDF, 0x10, 0xEF],  # Example NEC code
        device="tv",
        description="Turn TV on/off"
    )
    
    controller.add_command(tv_power)
    
    # Send command
    success = controller.send_command("tv_power")
    if success:
        print("Command sent successfully!")
    else:
        print("Failed to send command")
