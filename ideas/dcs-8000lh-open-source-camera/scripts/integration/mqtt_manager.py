#!/usr/bin/env python3
"""
MQTT Manager
Production-level MQTT broker management
"""

import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class MQTTManager:
    """MQTT broker management"""
    
    def __init__(self, config):
        self.config = config
        self.is_running = False
        
    def check_status(self) -> bool:
        """Check if MQTT broker is running"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=mqtt", "--format", "{{.Status}}"],
                capture_output=True,
                text=True
            )
            self.is_running = "Up" in result.stdout
            return self.is_running
        except Exception as e:
            logger.error(f"MQTT status check failed: {e}")
            return False
    
    def start_mqtt(self) -> bool:
        """Start MQTT broker"""
        try:
            logger.info("Starting MQTT broker...")
            result = subprocess.run(
                ["docker-compose", "up", "-d", "mqtt"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("MQTT broker started")
                return True
            else:
                logger.error(f"Failed to start MQTT: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to start MQTT: {e}")
            return False
