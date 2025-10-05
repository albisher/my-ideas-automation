"""
IR Protocol Handler for various TV remote control protocols
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

class IRProtocol(Enum):
    """Supported IR protocols"""
    NEC = "nec"
    RC5 = "rc5"
    RC6 = "rc6"
    PRONTO = "pronto"
    SAMSUNG = "samsung"
    LG = "lg"
    SONY = "sony"

class IRProtocolHandler:
    """
    Handles encoding and decoding of various IR protocols for TV control
    """
    
    def __init__(self, tv_config: Dict):
        """
        Initialize IR protocol handler
        
        Args:
            tv_config: TV configuration with protocol and codes
        """
        self.tv_config = tv_config
        self.protocol = tv_config.get('protocol', 'nec')
        self.codes = tv_config.get('codes', {})
        self.carrier_freq = tv_config.get('carrier_frequency', 38000)
        self.logger = logging.getLogger(__name__)
        
        # Protocol-specific timing parameters
        self.timing_params = self._get_timing_parameters()
    
    def _get_timing_parameters(self) -> Dict:
        """Get timing parameters for different protocols"""
        return {
            'nec': {
                'header_high': 9000,    # 9ms
                'header_low': 4500,     # 4.5ms
                'bit_0_high': 560,      # 560μs
                'bit_0_low': 560,       # 560μs
                'bit_1_high': 560,      # 560μs
                'bit_1_low': 1680,      # 1680μs
                'repeat_gap': 9000,     # 9ms
                'repeat_pulse': 2250,   # 2.25ms
                'carrier_freq': 38000   # 38kHz
            },
            'rc5': {
                'bit_time': 889,        # 889μs per bit
                'toggle_bit': True,     # RC5 has toggle bit
                'carrier_freq': 36000   # 36kHz
            },
            'rc6': {
                'bit_time': 444,        # 444μs per bit
                'mode_bits': 3,         # 3 mode bits
                'carrier_freq': 36000   # 36kHz
            }
        }
    
    def encode_command(self, command: str, parameters: Optional[Dict] = None) -> Optional[bytes]:
        """
        Encode a command into IR signal data
        
        Args:
            command: Command string (e.g., 'power', 'volume_up')
            parameters: Optional command parameters
            
        Returns:
            Encoded IR signal data or None if failed
        """
        try:
            # Get IR code for command
            ir_code = self._get_ir_code(command, parameters)
            if not ir_code:
                self.logger.error(f"No IR code found for command: {command}")
                return None
            
            # Encode based on protocol
            if self.protocol == 'nec':
                return self._encode_nec(ir_code)
            elif self.protocol == 'rc5':
                return self._encode_rc5(ir_code)
            elif self.protocol == 'rc6':
                return self._encode_rc6(ir_code)
            else:
                self.logger.error(f"Unsupported protocol: {self.protocol}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error encoding command '{command}': {e}")
            return None
    
    def _get_ir_code(self, command: str, parameters: Optional[Dict]) -> Optional[str]:
        """Get IR code for command"""
        # Handle parameterized commands
        if command == 'volume_set' and parameters:
            volume = parameters.get('volume', 50)
            # Map volume to specific codes or use volume up/down sequence
            return self._get_volume_code(volume)
        
        elif command == 'channel_set' and parameters:
            channel = parameters.get('channel', 1)
            # Map channel to specific codes or use channel up/down sequence
            return self._get_channel_code(channel)
        
        # Get code from configuration
        return self.codes.get(command)
    
    def _get_volume_code(self, volume: int) -> Optional[str]:
        """Get IR code for specific volume level"""
        # For most TVs, we use volume up/down commands
        # This could be enhanced to use specific volume codes if available
        if volume > 50:
            return self.codes.get('volume_up')
        else:
            return self.codes.get('volume_down')
    
    def _get_channel_code(self, channel: int) -> Optional[str]:
        """Get IR code for specific channel"""
        # For most TVs, we use channel up/down commands
        # This could be enhanced to use specific channel codes if available
        if channel > 10:
            return self.codes.get('channel_up')
        else:
            return self.codes.get('channel_down')
    
    def _encode_nec(self, ir_code: str) -> bytes:
        """
        Encode IR code using NEC protocol
        
        Args:
            ir_code: Hex string IR code (e.g., '0xE0E040BF')
            
        Returns:
            Encoded NEC signal data
        """
        try:
            # Parse hex code
            if ir_code.startswith('0x'):
                code = int(ir_code, 16)
            else:
                code = int(ir_code, 16)
            
            # NEC protocol: 16-bit address + 16-bit command
            address = (code >> 16) & 0xFFFF
            command = code & 0xFFFF
            
            # Generate timing data
            timing_data = []
            params = self.timing_params['nec']
            
            # Start pulse
            timing_data.extend([params['header_high'], params['header_low']])
            
            # Address (16 bits, LSB first)
            for i in range(16):
                bit = (address >> i) & 1
                if bit:
                    timing_data.extend([params['bit_1_high'], params['bit_1_low']])
                else:
                    timing_data.extend([params['bit_0_high'], params['bit_0_low']])
            
            # Command (16 bits, LSB first)
            for i in range(16):
                bit = (command >> i) & 1
                if bit:
                    timing_data.extend([params['bit_1_high'], params['bit_1_low']])
                else:
                    timing_data.extend([params['bit_0_high'], params['bit_0_low']])
            
            # End pulse
            timing_data.append(params['bit_0_high'])
            
            # Convert to bytes
            return self._timing_to_bytes(timing_data)
            
        except Exception as e:
            self.logger.error(f"Error encoding NEC code '{ir_code}': {e}")
            return None
    
    def _encode_rc5(self, ir_code: str) -> bytes:
        """
        Encode IR code using RC5 protocol
        
        Args:
            ir_code: Hex string IR code
            
        Returns:
            Encoded RC5 signal data
        """
        try:
            # Parse hex code
            if ir_code.startswith('0x'):
                code = int(ir_code, 16)
            else:
                code = int(ir_code, 16)
            
            # RC5 protocol: 14 bits total
            # Bit 0: Start bit (always 1)
            # Bit 1: Toggle bit
            # Bits 2-6: Address (5 bits)
            # Bits 7-13: Command (7 bits)
            
            timing_data = []
            params = self.timing_params['rc5']
            bit_time = params['bit_time']
            
            # Start bit (always 1)
            timing_data.extend([bit_time, bit_time])
            
            # Toggle bit (alternates on each transmission)
            toggle = int(time.time() * 2) % 2  # Simple toggle
            timing_data.extend([bit_time, bit_time] if toggle else [bit_time, bit_time])
            
            # Address and command bits
            for i in range(13, -1, -1):  # MSB first
                bit = (code >> i) & 1
                if bit:
                    timing_data.extend([bit_time, bit_time])
                else:
                    timing_data.extend([bit_time, bit_time])
            
            return self._timing_to_bytes(timing_data)
            
        except Exception as e:
            self.logger.error(f"Error encoding RC5 code '{ir_code}': {e}")
            return None
    
    def _encode_rc6(self, ir_code: str) -> bytes:
        """
        Encode IR code using RC6 protocol
        
        Args:
            ir_code: Hex string IR code
            
        Returns:
            Encoded RC6 signal data
        """
        try:
            # Parse hex code
            if ir_code.startswith('0x'):
                code = int(ir_code, 16)
            else:
                code = int(ir_code, 16)
            
            # RC6 protocol: 20 or 24 bits
            timing_data = []
            params = self.timing_params['rc6']
            bit_time = params['bit_time']
            
            # Start sequence
            timing_data.extend([6 * bit_time, 2 * bit_time])  # Leader
            timing_data.extend([bit_time, bit_time])          # Start bit
            
            # Mode bits (3 bits)
            mode = 0  # Mode 0 for standard RC6
            for i in range(2, -1, -1):
                bit = (mode >> i) & 1
                if bit:
                    timing_data.extend([2 * bit_time, bit_time])
                else:
                    timing_data.extend([bit_time, 2 * bit_time])
            
            # Data bits (16 bits)
            for i in range(15, -1, -1):
                bit = (code >> i) & 1
                if bit:
                    timing_data.extend([2 * bit_time, bit_time])
                else:
                    timing_data.extend([bit_time, 2 * bit_time])
            
            return self._timing_to_bytes(timing_data)
            
        except Exception as e:
            self.logger.error(f"Error encoding RC6 code '{ir_code}': {e}")
            return None
    
    def _timing_to_bytes(self, timing_data: List[int]) -> bytes:
        """
        Convert timing data to bytes for transmission
        
        Args:
            timing_data: List of timing values in microseconds
            
        Returns:
            Bytes representation of timing data
        """
        # Convert timing data to bytes
        # This is a simplified conversion - actual implementation would need
        # to convert to the specific format expected by the USB device
        
        byte_data = bytearray()
        
        for timing in timing_data:
            # Convert microseconds to device-specific units
            # This would need to be customized based on the USB device specs
            device_units = timing * 2  # Example conversion
            
            # Split into high and low bytes
            high_byte = (device_units >> 8) & 0xFF
            low_byte = device_units & 0xFF
            
            byte_data.extend([high_byte, low_byte])
        
        return bytes(byte_data)
    
    def decode_signal(self, signal_data: bytes) -> Optional[Dict]:
        """
        Decode received IR signal
        
        Args:
            signal_data: Raw IR signal data
            
        Returns:
            Decoded signal information or None if failed
        """
        try:
            # This would implement signal decoding logic
            # For now, return a placeholder
            return {
                'protocol': self.protocol,
                'decoded': True,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error decoding signal: {e}")
            return None
    
    def get_supported_protocols(self) -> List[str]:
        """Get list of supported IR protocols"""
        return [protocol.value for protocol in IRProtocol]
    
    def set_protocol(self, protocol: str):
        """Set IR protocol"""
        if protocol in [p.value for p in IRProtocol]:
            self.protocol = protocol
            self.logger.info(f"IR protocol set to: {protocol}")
        else:
            self.logger.error(f"Unsupported protocol: {protocol}")
    
    def add_custom_code(self, command: str, ir_code: str):
        """Add custom IR code for command"""
        self.codes[command] = ir_code
        self.logger.info(f"Added custom code for '{command}': {ir_code}")
    
    def get_available_commands(self) -> List[str]:
        """Get list of available commands with IR codes"""
        return list(self.codes.keys())

