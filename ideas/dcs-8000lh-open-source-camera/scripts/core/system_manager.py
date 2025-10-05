#!/usr/bin/env python3
"""
DCS-8000LH System Core Manager
Production-level core system management
"""

import os
import sys
import json
import time
import yaml
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Add system directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from communication.usb_communicator import USBCameraCommunicator
from integration.homeassistant_manager import HomeAssistantManager
from integration.mqtt_manager import MQTTManager
from integration.frigate_manager import FrigateManager
from monitoring.system_monitor import SystemMonitor

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
class SystemConfig:
    """System configuration structure"""
    camera_ip: str = "192.168.68.100"
    camera_username: str = "admin"
    camera_password: str = "admin"
    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    mqtt_username: str = "frigate"
    mqtt_password: str = "frigate_password"
    homeassistant_port: int = 8123
    frigate_port: int = 5001
    usb_port: str = "/dev/cu.usbserial-31130"
    baud_rate: int = 115200

class DCS8000LHSystemManager:
    """Main system manager for DCS-8000LH camera system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.usb_communicator = USBCameraCommunicator(self.config)
        self.homeassistant = HomeAssistantManager(self.config)
        self.mqtt_manager = MQTTManager(self.config)
        self.frigate_manager = FrigateManager(self.config)
        self.system_monitor = SystemMonitor(self.config)
        self.system_status = SystemStatus.INITIALIZING
        
    def _load_config(self, config_path: Optional[str]) -> SystemConfig:
        """Load system configuration"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                return SystemConfig(**config_data)
        return SystemConfig()
    
    def initialize_system(self) -> bool:
        """Initialize the complete DCS-8000LH system"""
        logger.info("Initializing DCS-8000LH system...")
        self.system_status = SystemStatus.INITIALIZING
        
        try:
            # Step 1: Connect to camera via USB-Serial
            logger.info("Step 1: Connecting to camera via USB-Serial...")
            if not self.usb_communicator.connect():
                logger.error("Failed to connect to camera")
                return False
            
            # Step 2: Get camera information
            logger.info("Step 2: Gathering camera information...")
            camera_info = self.usb_communicator.get_camera_info()
            if not camera_info:
                logger.error("Failed to get camera information")
                return False
            
            # Step 3: Configure camera network
            logger.info("Step 3: Configuring camera network...")
            if not self.usb_communicator.configure_network(
                self.config.camera_ip,
                "192.168.68.1",
                "8.8.8.8"
            ):
                logger.warning("Network configuration may have failed")
            
            # Step 4: Enable RTSP streaming
            logger.info("Step 4: Enabling RTSP streaming...")
            if not self.usb_communicator.enable_rtsp_stream():
                logger.warning("RTSP configuration may have failed")
            
            # Step 5: Start MQTT broker
            logger.info("Step 5: Starting MQTT broker...")
            if not self.mqtt_manager.start_mqtt():
                logger.error("Failed to start MQTT broker")
                return False
            
            # Step 6: Configure Frigate
            logger.info("Step 6: Configuring Frigate NVR...")
            if not self.frigate_manager.create_config(camera_info):
                logger.error("Failed to create Frigate configuration")
                return False
            
            if not self.frigate_manager.start_frigate():
                logger.error("Failed to start Frigate NVR")
                return False
            
            # Step 7: Configure Home Assistant
            logger.info("Step 7: Configuring Home Assistant...")
            if not self.homeassistant.create_configuration(camera_info):
                logger.error("Failed to create Home Assistant configuration")
                return False
            
            if not self.homeassistant.restart_homeassistant():
                logger.error("Failed to restart Home Assistant")
                return False
            
            self.system_status = SystemStatus.RUNNING
            logger.info("DCS-8000LH system initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            self.system_status = SystemStatus.ERROR
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "system_status": self.system_status.value,
            "camera_info": self.usb_communicator.camera_info.__dict__ if self.usb_communicator.camera_info else None,
            "homeassistant_running": self.homeassistant.check_status(),
            "mqtt_running": self.mqtt_manager.check_status(),
            "frigate_running": self.frigate_manager.check_status(),
            "usb_connected": self.usb_communicator.is_connected,
            "timestamp": datetime.now().isoformat()
        }
    
    def monitor_system(self, duration: int = 60):
        """Monitor system for specified duration"""
        logger.info(f"Starting system monitoring for {duration} seconds...")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            status = self.get_system_status()
            logger.info(f"System status: {status}")
            time.sleep(10)
        
        logger.info("System monitoring completed")
    
    def shutdown_system(self):
        """Shutdown the system gracefully"""
        logger.info("Shutting down DCS-8000LH system...")
        
        self.usb_communicator.disconnect()
        self.system_status = SystemStatus.MAINTENANCE
        
        logger.info("System shutdown completed")
