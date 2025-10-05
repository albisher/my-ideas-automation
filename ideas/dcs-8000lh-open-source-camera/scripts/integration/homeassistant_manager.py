#!/usr/bin/env python3
"""
Home Assistant Integration Manager
Production-level Home Assistant integration
"""

import os
import yaml
import requests
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class HomeAssistantManager:
    """Home Assistant integration manager"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = f"http://localhost:{config.homeassistant_port}"
        self.session = requests.Session()
        self.is_configured = False
        
    def check_status(self) -> bool:
        """Check if Home Assistant is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Home Assistant status check failed: {e}")
            return False
    
    def create_configuration(self, camera_info) -> bool:
        """Create comprehensive Home Assistant configuration"""
        logger.info("Creating Home Assistant configuration...")
        
        config_dir = Path("homeassistant/config")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Main configuration
        main_config = {
            "default_config": {},
            "mqtt": {
                "broker": self.config.mqtt_broker,
                "port": self.config.mqtt_port,
                "username": self.config.mqtt_username,
                "password": self.config.mqtt_password
            },
            "camera": [
                {
                    "platform": "generic",
                    "name": f"{camera_info.model} Camera",
                    "stream_source": f"rtsp://{self.config.camera_username}:{self.config.camera_password}@{camera_info.ip_address}:554/stream1",
                    "still_image_url": f"http://{camera_info.ip_address}/image.jpg",
                    "verify_ssl": False
                }
            ],
            "binary_sensor": [
                {
                    "platform": "template",
                    "sensors": {
                        f"{camera_info.model.lower().replace('-', '_')}_motion": {
                            "friendly_name": f"{camera_info.model} Motion",
                            "value_template": "{{ states('sensor.motion_detection') == 'on' }}",
                            "device_class": "motion"
                        }
                    }
                }
            ],
            "sensor": [
                {
                    "platform": "template",
                    "sensors": {
                        f"{camera_info.model.lower().replace('-', '_')}_person_count": {
                            "friendly_name": f"{camera_info.model} Person Count",
                            "value_template": "{{ states('sensor.person_detection_count') | default(0) }}",
                            "unit_of_measurement": "people"
                        },
                        f"{camera_info.model.lower().replace('-', '_')}_car_count": {
                            "friendly_name": f"{camera_info.model} Car Count",
                            "value_template": "{{ states('sensor.car_detection_count') | default(0) }}",
                            "unit_of_measurement": "cars"
                        }
                    }
                }
            ],
            "automation": "!include automations.yaml",
            "script": "!include scripts.yaml",
            "scene": "!include scenes.yaml",
            "group": "!include groups.yaml"
        }
        
        # Write main configuration
        with open(config_dir / "configuration.yaml", 'w') as f:
            yaml.dump(main_config, f, default_flow_style=False)
        
        # Create automations
        automations = [
            {
                "id": f"{camera_info.model.lower().replace('-', '_')}_motion_detected",
                "alias": f"{camera_info.model} Motion Detected",
                "description": f"Triggered when motion is detected on {camera_info.model}",
                "trigger": [
                    {
                        "platform": "state",
                        "entity_id": f"binary_sensor.{camera_info.model.lower().replace('-', '_')}_motion",
                        "to": "on"
                    }
                ],
                "action": [
                    {
                        "service": "notify.persistent_notification",
                        "data": {
                            "message": f"Motion detected on {camera_info.model}",
                            "title": "Security Alert",
                            "notification_id": f"{camera_info.model.lower().replace('-', '_')}_motion"
                        }
                    }
                ]
            }
        ]
        
        with open(config_dir / "automations.yaml", 'w') as f:
            yaml.dump(automations, f, default_flow_style=False)
        
        # Create empty include files
        for filename in ["scripts.yaml", "scenes.yaml", "groups.yaml"]:
            with open(config_dir / filename, 'w') as f:
                f.write("# Empty file\n")
        
        logger.info("Home Assistant configuration created")
        return True
    
    def restart_homeassistant(self) -> bool:
        """Restart Home Assistant container"""
        try:
            logger.info("Restarting Home Assistant...")
            result = subprocess.run(
                ["docker", "restart", "homeassistant"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("Home Assistant restarted successfully")
                return True
            else:
                logger.error(f"Home Assistant restart failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to restart Home Assistant: {e}")
            return False
