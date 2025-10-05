"""
USB HID Interface for FSP2C01915A remote control device
"""

import time
import logging
from typing import Optional, List, Tuple
import usb.core
import usb.util
import hid

class USBHIDInterface:
    """
    USB HID interface for communicating with FSP2C01915A remote control device
    """
    
    def __init__(self, device_id: str, vendor_id: Optional[int] = None, 
                 product_id: Optional[int] = None):
        """
        Initialize USB HID interface
        
        Args:
            device_id: Device identifier string (FSP2C01915A)
            vendor_id: USB vendor ID (optional, will auto-detect)
            product_id: USB product ID (optional, will auto-detect)
        """
        self.device_id = device_id
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = None
        self.hid_device = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize USB device
        self._initialize_device()
    
    def _initialize_device(self):
        """Initialize USB device connection"""
        try:
            # Try to find device by vendor/product ID if provided
            if self.vendor_id and self.product_id:
                self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
            else:
                # Auto-detect FSP2C01915A device
                self.device = self._find_fsp2c01915a_device()
            
            if self.device is None:
                raise ValueError(f"USB device {self.device_id} not found")
            
            # Set configuration
            self.device.set_configuration()
            
            # Initialize HID interface
            self._initialize_hid_interface()
            
            self.logger.info(f"USB HID interface initialized for device {self.device_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize USB device: {e}")
            raise
    
    def _find_fsp2c01915a_device(self) -> Optional[usb.core.Device]:
        """Find FSP2C01915A device by scanning USB devices"""
        try:
            # Get list of all USB devices
            devices = usb.core.find(find_all=True)
            
            for device in devices:
                try:
                    # Get device descriptor
                    descriptor = device.get_active_configuration()
                    
                    # Check for FSP2C01915A in device strings or descriptors
                    # This is a simplified check - actual implementation would need
                    # to examine the device's string descriptors
                    if self._is_fsp2c01915a_device(device):
                        return device
                        
                except Exception:
                    # Skip devices that can't be accessed
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error scanning for USB devices: {e}")
            return None
    
    def _is_fsp2c01915a_device(self, device: usb.core.Device) -> bool:
        """Check if device is FSP2C01915A based on descriptors"""
        try:
            # Get device descriptor
            descriptor = device.get_active_configuration()
            
            # Check interface class (should be HID)
            for interface in descriptor:
                if interface.bInterfaceClass == 3:  # HID class
                    # Additional checks for FSP2C01915A specific characteristics
                    # This would need to be customized based on actual device specs
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _initialize_hid_interface(self):
        """Initialize HID interface using hidapi"""
        try:
            # Use hidapi for HID communication
            devices = hid.enumerate()
            
            for device_info in devices:
                if self._matches_device_info(device_info):
                    self.hid_device = hid.device()
                    self.hid_device.open_path(device_info['path'])
                    break
            
            if self.hid_device is None:
                raise ValueError("HID device not found")
            
            self.logger.info("HID interface initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize HID interface: {e}")
            raise
    
    def _matches_device_info(self, device_info: dict) -> bool:
        """Check if device info matches FSP2C01915A"""
        # Check vendor ID, product ID, and other characteristics
        # This would need to be customized based on actual device specs
        return (
            device_info.get('usage_page') == 1 and  # Generic Desktop
            device_info.get('usage') == 6  # Keyboard
        )
    
    def send_ir_signal(self, ir_data: bytes) -> bool:
        """
        Send IR signal data to the remote control device
        
        Args:
            ir_data: IR signal data to transmit
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.hid_device is None:
                self.logger.error("HID device not initialized")
                return False
            
            # Prepare HID report for IR transmission
            report = self._prepare_ir_report(ir_data)
            
            # Send report to device
            result = self.hid_device.write(report)
            
            if result == len(report):
                self.logger.debug(f"IR signal sent successfully: {len(ir_data)} bytes")
                return True
            else:
                self.logger.error(f"Failed to send IR signal: {result} bytes written")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending IR signal: {e}")
            return False
    
    def _prepare_ir_report(self, ir_data: bytes) -> bytes:
        """
        Prepare HID report for IR signal transmission
        
        Args:
            ir_data: Raw IR signal data
            
        Returns:
            Formatted HID report
        """
        # HID report structure for FSP2C01915A
        # This would need to be customized based on actual device specifications
        
        report = bytearray(64)  # Standard HID report size
        
        # Report ID (first byte)
        report[0] = 0x01  # IR transmission report
        
        # IR data length
        report[1] = len(ir_data)
        
        # IR signal data
        data_length = min(len(ir_data), 60)  # Leave space for header
        report[2:2+data_length] = ir_data[:data_length]
        
        # Padding
        for i in range(2+data_length, 64):
            report[i] = 0x00
        
        return bytes(report)
    
    def read_button_states(self) -> Optional[List[int]]:
        """
        Read current button states from the remote control
        
        Returns:
            List of button states or None if failed
        """
        try:
            if self.hid_device is None:
                self.logger.error("HID device not initialized")
                return None
            
            # Read HID report
            report = self.hid_device.read(64)
            
            if report:
                # Parse button states from report
                button_states = self._parse_button_report(report)
                return button_states
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error reading button states: {e}")
            return None
    
    def _parse_button_report(self, report: bytes) -> List[int]:
        """
        Parse button states from HID report
        
        Args:
            report: HID report bytes
            
        Returns:
            List of button states
        """
        # Parse button states from HID report
        # This would need to be customized based on actual device report format
        
        button_states = []
        
        # Skip report ID (first byte)
        for i in range(1, min(len(report), 33)):  # Up to 32 buttons
            button_states.append(report[i])
        
        return button_states
    
    def get_device_info(self) -> dict:
        """
        Get device information
        
        Returns:
            Dictionary with device information
        """
        try:
            if self.hid_device is None:
                return {}
            
            return {
                'manufacturer': self.hid_device.get_manufacturer_string(),
                'product': self.hid_device.get_product_string(),
                'serial': self.hid_device.get_serial_number_string(),
                'device_id': self.device_id
            }
            
        except Exception as e:
            self.logger.error(f"Error getting device info: {e}")
            return {}
    
    def is_connected(self) -> bool:
        """
        Check if device is still connected
        
        Returns:
            True if connected, False otherwise
        """
        try:
            if self.hid_device is None:
                return False
            
            # Try to read device info to test connection
            self.hid_device.get_manufacturer_string()
            return True
            
        except Exception:
            return False
    
    def close(self):
        """Close USB HID interface and cleanup resources"""
        try:
            if self.hid_device:
                self.hid_device.close()
                self.hid_device = None
            
            if self.device:
                usb.util.dispose_resources(self.device)
                self.device = None
            
            self.logger.info("USB HID interface closed")
            
        except Exception as e:
            self.logger.error(f"Error closing USB interface: {e}")

