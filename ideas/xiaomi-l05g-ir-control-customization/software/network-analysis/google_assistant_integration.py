#!/usr/bin/env python3
"""
Google Assistant Integration for L05G
Direct integration with Google Assistant API for voice command automation
"""

import json
import time
import logging
import threading
import queue
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
import base64

class GoogleAssistantIntegration:
    """Google Assistant integration for L05G voice command automation"""
    
    def __init__(self, credentials_file: str = "google_credentials.json"):
        self.credentials_file = credentials_file
        self.credentials = self.load_credentials()
        self.logger = self.setup_logging()
        
        # Command management
        self.command_queue = queue.Queue()
        self.voice_commands = {}
        self.ir_commands = {}
        
        # Google Assistant API endpoints
        self.api_endpoints = {
            "assistant": "https://assistant.googleapis.com/v1",
            "speech": "https://speech.googleapis.com/v1",
            "text": "https://texttospeech.googleapis.com/v1"
        }
        
        # Voice command patterns
        self.voice_patterns = self.load_voice_patterns()
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("GoogleAssistantIntegration")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def load_credentials(self) -> Dict[str, Any]:
        """Load Google Assistant credentials"""
        try:
            with open(self.credentials_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Credentials file {self.credentials_file} not found")
            return {}
    
    def load_voice_patterns(self) -> Dict[str, List[str]]:
        """Load voice command patterns"""
        return {
            "device_control": {
                "tv": {
                    "power": ["turn on the tv", "turn off the tv", "switch on the tv", "switch off the tv"],
                    "volume": ["volume up", "volume down", "louder", "quieter", "mute", "unmute"],
                    "channel": ["next channel", "previous channel", "channel up", "channel down"]
                },
                "ac": {
                    "power": ["turn on the air conditioner", "turn off the air conditioner"],
                    "temperature": ["increase temperature", "decrease temperature", "hotter", "colder"],
                    "fan": ["fan speed up", "fan speed down", "change fan speed"]
                },
                "lights": {
                    "power": ["turn on the lights", "turn off the lights", "switch on the lights", "switch off the lights"],
                    "brightness": ["brighten the lights", "dim the lights", "increase brightness", "decrease brightness"]
                }
            }
        }
    
    def authenticate(self) -> bool:
        """Authenticate with Google Assistant API"""
        try:
            # Check if credentials are valid
            if not self.credentials:
                self.logger.error("No credentials available")
                return False
            
            # Test authentication with a simple request
            headers = {
                "Authorization": f"Bearer {self.credentials.get('access_token', '')}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.api_endpoints['assistant']}/devices",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("Successfully authenticated with Google Assistant API")
                return True
            else:
                self.logger.error(f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False
    
    def send_voice_command(self, command: str, device: str = None) -> bool:
        """Send voice command to Google Assistant"""
        try:
            # Format command for Google Assistant
            formatted_command = self.format_command(command, device)
            
            # Send command to Google Assistant
            success = self._send_to_assistant(formatted_command)
            
            if success:
                self.logger.info(f"Voice command sent: '{formatted_command}'")
                
                # Store command in database
                self._store_voice_command(command, device, formatted_command)
                
                return True
            else:
                self.logger.error(f"Failed to send voice command: '{formatted_command}'")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending voice command: {e}")
            return False
    
    def format_command(self, command: str, device: str = None) -> str:
        """Format command for Google Assistant"""
        if device and device in self.voice_patterns["device_control"]:
            device_commands = self.voice_patterns["device_control"][device]
            
            # Look for matching command pattern
            for action, patterns in device_commands.items():
                if command.lower() in [p.lower() for p in patterns]:
                    return f"Hey Google, {command}"
        
        # Default formatting
        return f"Hey Google, {command}"
    
    def _send_to_assistant(self, command: str) -> bool:
        """Send command to Google Assistant API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.get('access_token', '')}",
                "Content-Type": "application/json"
            }
            
            # Prepare request data
            request_data = {
                "text": command,
                "language_code": "en-US",
                "device_id": self.credentials.get("device_id", "l05g_device")
            }
            
            # Send request to Google Assistant
            response = requests.post(
                f"{self.api_endpoints['assistant']}/text:query",
                headers=headers,
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                # Parse response for IR command
                response_data = response.json()
                if self._contains_ir_command(response_data):
                    self._extract_ir_command(response_data)
                
                return True
            else:
                self.logger.error(f"Google Assistant API error: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending to Google Assistant: {e}")
            return False
    
    def _contains_ir_command(self, response_data: Dict[str, Any]) -> bool:
        """Check if response contains IR command"""
        try:
            # Look for IR command indicators in response
            response_text = json.dumps(response_data).lower()
            
            ir_indicators = [
                "ir", "infrared", "remote", "device control",
                "turn on", "turn off", "volume", "channel"
            ]
            
            return any(indicator in response_text for indicator in ir_indicators)
            
        except Exception as e:
            self.logger.error(f"Error checking for IR command: {e}")
            return False
    
    def _extract_ir_command(self, response_data: Dict[str, Any]):
        """Extract IR command from Google Assistant response"""
        try:
            # Extract IR command data
            ir_command = {
                "timestamp": datetime.now().isoformat(),
                "source": "google_assistant",
                "response": response_data,
                "ir_data": self._parse_ir_data(response_data)
            }
            
            # Store IR command
            command_id = f"ga_ir_{int(time.time())}"
            self.ir_commands[command_id] = ir_command
            
            self.logger.info(f"IR command extracted: {command_id}")
            
        except Exception as e:
            self.logger.error(f"Error extracting IR command: {e}")
    
    def _parse_ir_data(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse IR data from Google Assistant response"""
        try:
            # Extract relevant IR command information
            ir_data = {
                "device": self._extract_device_name(response_data),
                "command": self._extract_command_name(response_data),
                "parameters": self._extract_command_parameters(response_data)
            }
            
            return ir_data
            
        except Exception as e:
            self.logger.error(f"Error parsing IR data: {e}")
            return {}
    
    def _extract_device_name(self, response_data: Dict[str, Any]) -> str:
        """Extract device name from response"""
        try:
            # Look for device name in response
            response_text = json.dumps(response_data).lower()
            
            devices = ["tv", "television", "ac", "air conditioner", "lights", "fan"]
            for device in devices:
                if device in response_text:
                    return device
            
            return "unknown"
            
        except Exception as e:
            self.logger.error(f"Error extracting device name: {e}")
            return "unknown"
    
    def _extract_command_name(self, response_data: Dict[str, Any]) -> str:
        """Extract command name from response"""
        try:
            # Look for command name in response
            response_text = json.dumps(response_data).lower()
            
            commands = ["turn on", "turn off", "volume up", "volume down", "channel up", "channel down"]
            for command in commands:
                if command in response_text:
                    return command
            
            return "unknown"
            
        except Exception as e:
            self.logger.error(f"Error extracting command name: {e}")
            return "unknown"
    
    def _extract_command_parameters(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract command parameters from response"""
        try:
            # Extract command parameters
            parameters = {
                "timestamp": datetime.now().isoformat(),
                "source": "google_assistant",
                "raw_response": response_data
            }
            
            return parameters
            
        except Exception as e:
            self.logger.error(f"Error extracting command parameters: {e}")
            return {}
    
    def _store_voice_command(self, command: str, device: str, formatted_command: str):
        """Store voice command in database"""
        try:
            voice_command = {
                "timestamp": datetime.now().isoformat(),
                "original_command": command,
                "device": device,
                "formatted_command": formatted_command,
                "source": "google_assistant"
            }
            
            command_id = f"ga_voice_{int(time.time())}"
            self.voice_commands[command_id] = voice_command
            
        except Exception as e:
            self.logger.error(f"Error storing voice command: {e}")
    
    def queue_command(self, command: str, device: str = None):
        """Queue command for later execution"""
        try:
            command_data = {
                "command": command,
                "device": device,
                "timestamp": datetime.now().isoformat()
            }
            
            self.command_queue.put(command_data)
            self.logger.info(f"Command queued: {command}")
            
        except Exception as e:
            self.logger.error(f"Error queuing command: {e}")
    
    def process_command_queue(self):
        """Process queued commands"""
        try:
            while not self.command_queue.empty():
                command_data = self.command_queue.get_nowait()
                
                # Send command to Google Assistant
                success = self.send_voice_command(
                    command_data["command"],
                    command_data["device"]
                )
                
                if success:
                    self.logger.info(f"Processed queued command: {command_data['command']}")
                else:
                    self.logger.error(f"Failed to process queued command: {command_data['command']}")
                
                # Wait between commands
                time.sleep(2)
                
        except queue.Empty:
            pass
        except Exception as e:
            self.logger.error(f"Error processing command queue: {e}")
    
    def start_command_processor(self):
        """Start background command processor"""
        def processor():
            while True:
                self.process_command_queue()
                time.sleep(1)
        
        thread = threading.Thread(target=processor, daemon=True)
        thread.start()
        self.logger.info("Command processor started")
    
    def get_voice_commands(self) -> Dict[str, Any]:
        """Get all voice commands"""
        return self.voice_commands
    
    def get_ir_commands(self) -> Dict[str, Any]:
        """Get all IR commands"""
        return self.ir_commands
    
    def save_commands(self):
        """Save commands to file"""
        try:
            # Save voice commands
            with open("voice_commands.json", 'w') as f:
                json.dump(self.voice_commands, f, indent=2)
            
            # Save IR commands
            with open("ir_commands.json", 'w') as f:
                json.dump(self.ir_commands, f, indent=2)
            
            self.logger.info("Commands saved to files")
            
        except Exception as e:
            self.logger.error(f"Error saving commands: {e}")
    
    def load_commands(self):
        """Load commands from file"""
        try:
            # Load voice commands
            with open("voice_commands.json", 'r') as f:
                self.voice_commands = json.load(f)
            
            # Load IR commands
            with open("ir_commands.json", 'r') as f:
                self.ir_commands = json.load(f)
            
            self.logger.info("Commands loaded from files")
            
        except FileNotFoundError:
            self.logger.info("No existing command files found")
        except Exception as e:
            self.logger.error(f"Error loading commands: {e}")

# Example usage
if __name__ == "__main__":
    # Initialize Google Assistant integration
    ga_integration = GoogleAssistantIntegration("google_credentials.json")
    
    # Authenticate
    if ga_integration.authenticate():
        print("Successfully authenticated with Google Assistant")
        
        # Start command processor
        ga_integration.start_command_processor()
        
        # Send voice commands
        ga_integration.send_voice_command("turn on the tv", "tv")
        time.sleep(3)
        ga_integration.send_voice_command("volume up", "tv")
        time.sleep(3)
        ga_integration.send_voice_command("turn on the air conditioner", "ac")
        
        # Get commands
        voice_commands = ga_integration.get_voice_commands()
        ir_commands = ga_integration.get_ir_commands()
        
        print(f"Voice commands: {len(voice_commands)}")
        print(f"IR commands: {len(ir_commands)}")
        
        # Save commands
        ga_integration.save_commands()
        
    else:
        print("Failed to authenticate with Google Assistant")
