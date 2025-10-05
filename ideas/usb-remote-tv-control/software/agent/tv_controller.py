"""
TV Controller Agent - Core intelligence for USB remote TV control
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TVState(Enum):
    """TV power states"""
    UNKNOWN = "unknown"
    ON = "on"
    OFF = "off"
    STANDBY = "standby"

class CommandType(Enum):
    """Available TV control commands"""
    POWER = "power"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    VOLUME_SET = "volume_set"
    CHANNEL_UP = "channel_up"
    CHANNEL_DOWN = "channel_down"
    CHANNEL_SET = "channel_set"
    INPUT_HDMI1 = "input_hdmi1"
    INPUT_HDMI2 = "input_hdmi2"
    INPUT_HDMI3 = "input_hdmi3"
    INPUT_HDMI4 = "input_hdmi4"
    INPUT_USB = "input_usb"
    INPUT_AV = "input_av"
    MUTE = "mute"
    MENU = "menu"
    BACK = "back"
    HOME = "home"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    OK = "ok"
    EXIT = "exit"

@dataclass
class CommandResult:
    """Result of a TV control command"""
    success: bool
    command: str
    timestamp: float
    error_message: Optional[str] = None
    tv_state_change: bool = False

@dataclass
class TVStatus:
    """Current TV status"""
    power_state: TVState
    volume: int
    channel: int
    input_source: str
    last_command: Optional[str]
    last_command_time: Optional[float]

class TVController:
    """
    Main TV control agent that interfaces with USB remote control
    """
    
    def __init__(self, usb_device_id: str, tv_config: Dict, 
                 learning_enabled: bool = True, debug: bool = False):
        """
        Initialize TV controller agent
        
        Args:
            usb_device_id: USB device identifier (FSP2C01915A)
            tv_config: TV configuration dictionary
            learning_enabled: Enable machine learning features
            debug: Enable debug logging
        """
        self.usb_device_id = usb_device_id
        self.tv_config = tv_config
        self.learning_enabled = learning_enabled
        self.debug = debug
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        
        # Initialize components
        self.usb_interface = None
        self.protocol_handler = None
        self.state_manager = None
        self.learning_engine = None
        
        # TV state tracking
        self.current_status = TVStatus(
            power_state=TVState.UNKNOWN,
            volume=50,
            channel=1,
            input_source="hdmi1",
            last_command=None,
            last_command_time=None
        )
        
        # Command history for learning
        self.command_history: List[Tuple[str, float, bool]] = []
        
        # Initialize system
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize USB interface and protocol handler"""
        try:
            # Initialize USB HID interface
            from .usb_driver.usb_hid_interface import USBHIDInterface
            self.usb_interface = USBHIDInterface(self.usb_device_id)
            
            # Initialize protocol handler
            from .protocol_handler.ir_protocols import IRProtocolHandler
            self.protocol_handler = IRProtocolHandler(self.tv_config)
            
            # Initialize state manager
            from .state_manager import StateManager
            self.state_manager = StateManager(self.current_status)
            
            # Initialize learning engine if enabled
            if self.learning_enabled:
                from .learning_engine import LearningEngine
                self.learning_engine = LearningEngine()
            
            self.logger.info("TV Controller initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TV Controller: {e}")
            raise
    
    def send_command(self, command: str, parameters: Optional[Dict] = None) -> CommandResult:
        """
        Send a command to the TV via USB remote control
        
        Args:
            command: Command string (e.g., 'power', 'volume_up', 'channel_set')
            parameters: Optional command parameters (e.g., {'volume': 25})
            
        Returns:
            CommandResult object with success status and details
        """
        start_time = time.time()
        
        try:
            # Validate command
            if not self._validate_command(command, parameters):
                return CommandResult(
                    success=False,
                    command=command,
                    timestamp=start_time,
                    error_message="Invalid command or parameters"
                )
            
            # Process command through learning engine if enabled
            if self.learning_enabled and self.learning_engine:
                command = self.learning_engine.process_command(command, parameters)
            
            # Generate IR signal for command
            ir_signal = self.protocol_handler.encode_command(command, parameters)
            if not ir_signal:
                return CommandResult(
                    success=False,
                    command=command,
                    timestamp=start_time,
                    error_message="Failed to generate IR signal"
                )
            
            # Send command via USB interface
            success = self.usb_interface.send_ir_signal(ir_signal)
            if not success:
                return CommandResult(
                    success=False,
                    command=command,
                    timestamp=start_time,
                    error_message="Failed to send IR signal via USB"
                )
            
            # Update TV state
            self._update_tv_state(command, parameters)
            
            # Record command in history
            self.command_history.append((command, start_time, True))
            
            # Update learning engine
            if self.learning_enabled and self.learning_engine:
                self.learning_engine.record_successful_command(command, parameters)
            
            self.logger.info(f"Command '{command}' executed successfully")
            
            return CommandResult(
                success=True,
                command=command,
                timestamp=start_time,
                tv_state_change=True
            )
            
        except Exception as e:
            self.logger.error(f"Command '{command}' failed: {e}")
            
            # Record failed command
            self.command_history.append((command, start_time, False))
            
            return CommandResult(
                success=False,
                command=command,
                timestamp=start_time,
                error_message=str(e)
            )
    
    def _validate_command(self, command: str, parameters: Optional[Dict]) -> bool:
        """Validate command and parameters"""
        try:
            # Check if command is supported
            if command not in [cmd.value for cmd in CommandType]:
                self.logger.warning(f"Unsupported command: {command}")
                return False
            
            # Validate parameters for specific commands
            if command == "volume_set" and parameters:
                volume = parameters.get("volume", 0)
                if not isinstance(volume, int) or volume < 0 or volume > 100:
                    self.logger.warning(f"Invalid volume parameter: {volume}")
                    return False
            
            elif command == "channel_set" and parameters:
                channel = parameters.get("channel", 0)
                if not isinstance(channel, int) or channel < 1:
                    self.logger.warning(f"Invalid channel parameter: {channel}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Command validation failed: {e}")
            return False
    
    def _update_tv_state(self, command: str, parameters: Optional[Dict]):
        """Update internal TV state based on command"""
        try:
            if command == "power":
                if self.current_status.power_state == TVState.OFF:
                    self.current_status.power_state = TVState.ON
                else:
                    self.current_status.power_state = TVState.OFF
            
            elif command == "volume_set" and parameters:
                self.current_status.volume = parameters.get("volume", self.current_status.volume)
            
            elif command == "volume_up":
                self.current_status.volume = min(100, self.current_status.volume + 1)
            
            elif command == "volume_down":
                self.current_status.volume = max(0, self.current_status.volume - 1)
            
            elif command == "channel_set" and parameters:
                self.current_status.channel = parameters.get("channel", self.current_status.channel)
            
            elif command == "channel_up":
                self.current_status.channel += 1
            
            elif command == "channel_down":
                self.current_status.channel = max(1, self.current_status.channel - 1)
            
            elif command.startswith("input_"):
                self.current_status.input_source = command.replace("input_", "")
            
            # Update last command info
            self.current_status.last_command = command
            self.current_status.last_command_time = time.time()
            
            # Update state manager
            if self.state_manager:
                self.state_manager.update_status(self.current_status)
            
        except Exception as e:
            self.logger.error(f"Failed to update TV state: {e}")
    
    def get_tv_status(self) -> TVStatus:
        """Get current TV status"""
        return self.current_status
    
    def get_command_history(self, limit: int = 10) -> List[Tuple[str, float, bool]]:
        """Get recent command history"""
        return self.command_history[-limit:] if self.command_history else []
    
    def learn_from_user_behavior(self, user_commands: List[Tuple[str, float]]):
        """Learn from user behavior patterns"""
        if self.learning_enabled and self.learning_engine:
            self.learning_engine.learn_from_behavior(user_commands)
    
    def shutdown(self):
        """Shutdown the TV controller and cleanup resources"""
        try:
            if self.usb_interface:
                self.usb_interface.close()
            
            if self.state_manager:
                self.state_manager.save_state()
            
            self.logger.info("TV Controller shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

