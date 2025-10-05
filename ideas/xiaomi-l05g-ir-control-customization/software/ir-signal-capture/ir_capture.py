#!/usr/bin/env python3
"""
IR Signal Capture for Xiaomi L05G
Captures IR signals from L05G and creates command database
"""

import RPi.GPIO as GPIO
import time
import json
import numpy as np
from typing import List, Dict, Any
import logging

class IRCapture:
    """IR signal capture and analysis"""
    
    def __init__(self, ir_pin: int = 18, sample_rate: float = 0.0001):
        self.ir_pin = ir_pin
        self.sample_rate = sample_rate
        self.logger = self.setup_logging()
        self.setup_gpio()
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("IRCapture")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def setup_gpio(self):
        """Setup GPIO for IR receiver"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ir_pin, GPIO.IN)
        self.logger.info(f"GPIO setup complete on pin {self.ir_pin}")
    
    def capture_signal(self, duration: float = 5.0) -> List[int]:
        """Capture IR signal for specified duration"""
        self.logger.info(f"Capturing IR signal for {duration} seconds...")
        
        signal = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            if GPIO.input(self.ir_pin):
                signal.append(1)
            else:
                signal.append(0)
            time.sleep(self.sample_rate)
        
        self.logger.info(f"Captured {len(signal)} samples")
        return signal
    
    def analyze_signal(self, signal: List[int]) -> Dict[str, Any]:
        """Analyze captured IR signal"""
        # Convert to numpy array for analysis
        signal_array = np.array(signal)
        
        # Find signal transitions
        transitions = np.where(np.diff(signal_array) != 0)[0]
        
        # Calculate pulse durations
        pulse_durations = []
        for i in range(len(transitions) - 1):
            duration = (transitions[i + 1] - transitions[i]) * self.sample_rate
            pulse_durations.append(duration)
        
        # Analyze signal characteristics
        analysis = {
            "total_samples": len(signal),
            "duration": len(signal) * self.sample_rate,
            "transitions": len(transitions),
            "pulse_durations": pulse_durations,
            "signal_type": self.identify_signal_type(pulse_durations),
            "raw_signal": signal
        }
        
        return analysis
    
    def identify_signal_type(self, pulse_durations: List[float]) -> str:
        """Identify IR signal protocol type"""
        if not pulse_durations:
            return "unknown"
        
        # Analyze pulse patterns
        short_pulses = [p for p in pulse_durations if p < 0.001]  # < 1ms
        long_pulses = [p for p in pulse_durations if p >= 0.001]   # >= 1ms
        
        if len(short_pulses) > len(long_pulses) * 2:
            return "nec"
        elif len(long_pulses) > len(short_pulses) * 2:
            return "rc5"
        else:
            return "raw"
    
    def save_signal(self, signal: List[int], filename: str):
        """Save captured signal to file"""
        with open(filename, 'w') as f:
            json.dump(signal, f)
        self.logger.info(f"Signal saved to {filename}")
    
    def load_signal(self, filename: str) -> List[int]:
        """Load signal from file"""
        with open(filename, 'r') as f:
            signal = json.load(f)
        self.logger.info(f"Signal loaded from {filename}")
        return signal
    
    def create_command_database(self, signals: Dict[str, List[int]]) -> Dict[str, Any]:
        """Create IR command database from captured signals"""
        database = {}
        
        for command_name, signal in signals.items():
            analysis = self.analyze_signal(signal)
            database[command_name] = {
                "signal": signal,
                "analysis": analysis,
                "timestamp": time.time()
            }
        
        return database
    
    def save_database(self, database: Dict[str, Any], filename: str):
        """Save IR command database to file"""
        with open(filename, 'w') as f:
            json.dump(database, f, indent=2)
        self.logger.info(f"Database saved to {filename}")
    
    def load_database(self, filename: str) -> Dict[str, Any]:
        """Load IR command database from file"""
        with open(filename, 'r') as f:
            database = json.load(f)
        self.logger.info(f"Database loaded from {filename}")
        return database

class L05GController:
    """Controller for Xiaomi L05G IR signal capture"""
    
    def __init__(self):
        self.ir_capture = IRCapture()
        self.logger = self.ir_capture.logger
    
    def learn_command(self, command_name: str, device_name: str) -> bool:
        """Learn IR command from L05G"""
        self.logger.info(f"Learning command '{command_name}' for device '{device_name}'")
        self.logger.info("Trigger the command on your L05G now...")
        
        # Capture signal
        signal = self.ir_capture.capture_signal(duration=5.0)
        
        if not signal:
            self.logger.error("No signal captured")
            return False
        
        # Analyze signal
        analysis = self.ir_capture.analyze_signal(signal)
        
        if analysis["transitions"] < 10:
            self.logger.error("Signal too weak or no signal detected")
            return False
        
        # Save command
        command_data = {
            "name": command_name,
            "device": device_name,
            "signal": signal,
            "analysis": analysis,
            "timestamp": time.time()
        }
        
        # Save to database
        self.save_command(command_data)
        
        self.logger.info(f"Successfully learned command: {command_name}")
        return True
    
    def save_command(self, command_data: Dict[str, Any]):
        """Save learned command to database"""
        try:
            # Load existing database
            database = self.ir_capture.load_database("ir_commands.json")
        except FileNotFoundError:
            database = {}
        
        # Add new command
        database[command_data["name"]] = command_data
        
        # Save updated database
        self.ir_capture.save_database(database, "ir_commands.json")
    
    def list_commands(self) -> List[str]:
        """List available commands"""
        try:
            database = self.ir_capture.load_database("ir_commands.json")
            return list(database.keys())
        except FileNotFoundError:
            return []
    
    def get_command(self, command_name: str) -> Dict[str, Any]:
        """Get command data"""
        try:
            database = self.ir_capture.load_database("ir_commands.json")
            return database.get(command_name, {})
        except FileNotFoundError:
            return {}

# Example usage
if __name__ == "__main__":
    controller = L05GController()
    
    # Learn a command
    success = controller.learn_command("tv_power", "tv")
    if success:
        print("Command learned successfully!")
    else:
        print("Failed to learn command")
    
    # List available commands
    commands = controller.list_commands()
    print(f"Available commands: {commands}")
