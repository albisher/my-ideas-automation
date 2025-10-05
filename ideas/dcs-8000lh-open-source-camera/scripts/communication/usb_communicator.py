#!/usr/bin/env python3
"""
USB-Serial Communication Module for DCS-8000LH Camera
Production-level USB communication system
"""

import serial
import time
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SystemStatus(Enum):
    """System status enumeration"""
    INITIALIZING = "initializing"
    CONNECTING = "connecting"
    CONFIGURING = "configuring"
    RUNNING = "running"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class CameraInfo:
    """Camera information structure"""
    model: str
    serial_number: str
    firmware_version: str
    ip_address: str
    mac_address: str
    status: SystemStatus
    last_seen: datetime
    capabilities: List[str]

class USBCameraCommunicator:
    """USB-Serial communication with DCS-8000LH camera"""
    
    def __init__(self, config):
        self.config = config
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False
        self.camera_info: Optional[CameraInfo] = None
        
    def connect(self) -> bool:
        """Establish USB-Serial connection with camera"""
        try:
            logger.info(f"Connecting to camera via USB-Serial at {self.config.usb_port}")
            self.serial_connection = serial.Serial(
                port=self.config.usb_port,
                baudrate=self.config.baud_rate,
                timeout=2,
                write_timeout=2
            )
            self.is_connected = True
            logger.info("USB-Serial connection established")
            return True
        except Exception as e:
            logger.error(f"Failed to connect via USB-Serial: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from camera"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            logger.info("USB-Serial connection closed")
    
    def send_command(self, command: str, timeout: int = 3) -> Optional[str]:
        """Send command to camera and get response"""
        if not self.is_connected or not self.serial_connection:
            logger.error("Not connected to camera")
            return None
        
        try:
            logger.debug(f"Sending command: {command}")
            self.serial_connection.write(f"{command}\r\n".encode())
            time.sleep(timeout)
            
            response = self.serial_connection.read(1024).decode('utf-8', errors='ignore')
            logger.debug(f"Received response: {response}")
            return response
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return None
    
    def get_camera_info(self) -> Optional[CameraInfo]:
        """Get comprehensive camera information"""
        if not self.is_connected:
            return None
        
        logger.info("Gathering camera information...")
        
        # Get system information
        version_info = self.send_command("cat /proc/version")
        cpu_info = self.send_command("cat /proc/cpuinfo")
        memory_info = self.send_command("cat /proc/meminfo")
        network_info = self.send_command("ifconfig")
        hostname = self.send_command("cat /etc/hostname")
        
        # Parse information
        model = "DCS-8000LH"
        serial_number = "Unknown"
        firmware_version = "Unknown"
        ip_address = self.config.camera_ip
        mac_address = "Unknown"
        
        if version_info:
            firmware_version = version_info.split()[2] if len(version_info.split()) > 2 else "Unknown"
        
        if network_info:
            # Extract MAC address from network info
            for line in network_info.split('\n'):
                if 'HWaddr' in line or 'ether' in line:
                    mac_address = line.split()[-1]
                    break
        
        if hostname:
            serial_number = hostname.strip()
        
        # Determine capabilities
        capabilities = []
        if self.send_command("which ffmpeg"):
            capabilities.append("video_encoding")
        if self.send_command("which motion"):
            capabilities.append("motion_detection")
        if self.send_command("which iptables"):
            capabilities.append("firewall")
        
        self.camera_info = CameraInfo(
            model=model,
            serial_number=serial_number,
            firmware_version=firmware_version,
            ip_address=ip_address,
            mac_address=mac_address,
            status=SystemStatus.RUNNING,
            last_seen=datetime.now(),
            capabilities=capabilities
        )
        
        logger.info(f"Camera info gathered: {self.camera_info}")
        return self.camera_info
    
    def configure_network(self, ip_address: str, gateway: str, dns: str) -> bool:
        """Configure camera network settings"""
        if not self.is_connected:
            return False
        
        logger.info(f"Configuring network: IP={ip_address}, Gateway={gateway}, DNS={dns}")
        
        commands = [
            f"ifconfig eth0 {ip_address} netmask 255.255.255.0",
            f"route add default gw {gateway}",
            f"echo 'nameserver {dns}' > /etc/resolv.conf"
        ]
        
        for cmd in commands:
            result = self.send_command(cmd)
            if not result:
                logger.error(f"Network configuration failed: {cmd}")
                return False
        
        logger.info("Network configuration completed")
        return True
    
    def enable_rtsp_stream(self) -> bool:
        """Enable RTSP streaming on camera"""
        if not self.is_connected:
            return False
        
        logger.info("Enabling RTSP streaming...")
        
        # Enable RTSP service
        rtsp_commands = [
            "killall rtspd",
            "rtspd -p 554 -m 8554",
            "echo 'rtspd enabled' > /tmp/rtsp_status"
        ]
        
        for cmd in rtsp_commands:
            result = self.send_command(cmd)
            if not result:
                logger.warning(f"RTSP command may have failed: {cmd}")
        
        logger.info("RTSP streaming enabled")
        return True
