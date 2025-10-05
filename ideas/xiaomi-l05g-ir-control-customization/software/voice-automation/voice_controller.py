#!/usr/bin/env python3
"""
Voice Command Automation for Xiaomi L05G
Uses TTS to send voice commands to L05G for IR control
"""

import pyttsx3
import time
import json
import logging
from typing import Dict, List, Any
import threading
import queue

class VoiceController:
    """Voice command controller for L05G"""
    
    def __init__(self, config_file: str = "voice_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.logger = self.setup_logging()
        self.setup_tts()
        self.command_queue = queue.Queue()
        self.is_speaking = False
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("VoiceController")
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
            "tts": {
                "rate": 150,
                "volume": 0.8,
                "voice": "english"
            },
            "l05g": {
                "response_delay": 2.0,
                "command_timeout": 10.0
            },
            "devices": {
                "tv": {
                    "power": "Turn on the TV",
                    "volume_up": "Increase TV volume",
                    "volume_down": "Decrease TV volume",
                    "channel_up": "Next channel",
                    "channel_down": "Previous channel"
                },
                "ac": {
                    "power": "Turn on the air conditioner",
                    "temp_up": "Increase AC temperature",
                    "temp_down": "Decrease AC temperature",
                    "fan_speed": "Change AC fan speed"
                }
            }
        }
    
    def setup_tts(self):
        """Setup text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS settings
            rate = self.config.get("tts", {}).get("rate", 150)
            volume = self.config.get("tts", {}).get("volume", 0.8)
            
            self.tts_engine.setProperty('rate', rate)
            self.tts_engine.setProperty('volume', volume)
            
            # Set voice
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)
            
            self.logger.info("TTS engine initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS: {e}")
            self.tts_engine = None
    
    def speak(self, text: str) -> bool:
        """Speak text using TTS"""
        if not self.tts_engine:
            self.logger.error("TTS engine not available")
            return False
        
        try:
            self.is_speaking = True
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            self.is_speaking = False
            return True
            
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
            self.is_speaking = False
            return False
    
    def send_voice_command(self, command: str, device: str = None) -> bool:
        """Send voice command to L05G"""
        if not command:
            self.logger.error("No command specified")
            return False
        
        self.logger.info(f"Sending voice command: '{command}'")
        
        # Speak the command
        success = self.speak(command)
        
        if success:
            # Wait for L05G to process
            response_delay = self.config.get("l05g", {}).get("response_delay", 2.0)
            time.sleep(response_delay)
            self.logger.info("Voice command sent successfully")
        else:
            self.logger.error("Failed to send voice command")
        
        return success
    
    def send_device_command(self, device: str, action: str) -> bool:
        """Send device-specific command"""
        device_commands = self.config.get("devices", {}).get(device, {})
        
        if action not in device_commands:
            self.logger.error(f"Unknown action '{action}' for device '{device}'")
            return False
        
        command = device_commands[action]
        return self.send_voice_command(command, device)
    
    def add_device_command(self, device: str, action: str, command: str):
        """Add new device command"""
        if "devices" not in self.config:
            self.config["devices"] = {}
        
        if device not in self.config["devices"]:
            self.config["devices"][device] = {}
        
        self.config["devices"][device][action] = command
        self.save_config()
        self.logger.info(f"Added command: {device}.{action} -> '{command}'")
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def list_devices(self) -> List[str]:
        """List available devices"""
        return list(self.config.get("devices", {}).keys())
    
    def list_device_commands(self, device: str) -> List[str]:
        """List commands for specific device"""
        device_commands = self.config.get("devices", {}).get(device, {})
        return list(device_commands.keys())
    
    def queue_command(self, command: str, device: str = None):
        """Queue command for later execution"""
        self.command_queue.put({
            "command": command,
            "device": device,
            "timestamp": time.time()
        })
        self.logger.info(f"Command queued: '{command}'")
    
    def process_command_queue(self):
        """Process queued commands"""
        while not self.command_queue.empty():
            try:
                cmd_data = self.command_queue.get_nowait()
                self.send_voice_command(cmd_data["command"], cmd_data["device"])
            except queue.Empty:
                break
            except Exception as e:
                self.logger.error(f"Error processing queued command: {e}")
    
    def start_command_processor(self):
        """Start background command processor"""
        def processor():
            while True:
                self.process_command_queue()
                time.sleep(0.1)
        
        thread = threading.Thread(target=processor, daemon=True)
        thread.start()
        self.logger.info("Command processor started")

class L05GVoiceController:
    """Main controller for L05G voice automation"""
    
    def __init__(self):
        self.voice_controller = VoiceController()
        self.logger = self.voice_controller.logger
    
    def control_tv(self, action: str) -> bool:
        """Control TV via voice commands"""
        return self.voice_controller.send_device_command("tv", action)
    
    def control_ac(self, action: str) -> bool:
        """Control AC via voice commands"""
        return self.voice_controller.send_device_command("ac", action)
    
    def send_custom_command(self, command: str) -> bool:
        """Send custom voice command"""
        return self.voice_controller.send_voice_command(command)
    
    def learn_new_command(self, device: str, action: str, command: str):
        """Learn new voice command"""
        self.voice_controller.add_device_command(device, action, command)
    
    def get_available_commands(self) -> Dict[str, List[str]]:
        """Get all available commands"""
        commands = {}
        for device in self.voice_controller.list_devices():
            commands[device] = self.voice_controller.list_device_commands(device)
        return commands

# Example usage
if __name__ == "__main__":
    controller = L05GVoiceController()
    
    # Control TV
    controller.control_tv("power")
    time.sleep(3)
    controller.control_tv("volume_up")
    
    # Control AC
    controller.control_ac("power")
    time.sleep(3)
    controller.control_ac("temp_up")
    
    # Send custom command
    controller.send_custom_command("Turn on the lights")
    
    # Learn new command
    controller.learn_new_command("tv", "mute", "Mute the TV")
    
    # Get available commands
    commands = controller.get_available_commands()
    print(f"Available commands: {commands}")
