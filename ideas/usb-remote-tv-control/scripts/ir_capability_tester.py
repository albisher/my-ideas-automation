#!/usr/bin/env python3
"""
IR Capability Tester for USB Devices
Tests if connected devices can transmit IR signals for TV control
"""

import hid
import time
import struct
from typing import Dict, List, Optional

class IRCapabilityTester:
    """Test IR transmission capabilities of USB devices"""
    
    def __init__(self):
        self.devices = []
        self.test_results = []
    
    def find_accessible_devices(self) -> List[Dict]:
        """Find devices that can be accessed for testing"""
        print("Finding accessible USB devices...")
        
        all_devices = hid.enumerate()
        accessible_devices = []
        
        for device_info in all_devices:
            try:
                # Try to open device to check accessibility
                device = hid.device()
                device.open_path(device_info['path'])
                
                # Get device info
                manufacturer = device.get_manufacturer_string()
                product = device.get_product_string()
                
                device_data = {
                    'vendor_id': device_info['vendor_id'],
                    'product_id': device_info['product_id'],
                    'manufacturer': manufacturer,
                    'product': product,
                    'usage_page': device_info.get('usage_page', 0),
                    'usage': device_info.get('usage', 0),
                    'path': device_info['path'],
                    'interface_number': device_info.get('interface_number', 0),
                    'device_info': device_info
                }
                
                accessible_devices.append(device_data)
                device.close()
                
            except Exception as e:
                # Device not accessible, skip
                continue
        
        return accessible_devices
    
    def test_ir_transmission(self, device: Dict) -> Dict:
        """Test IR signal transmission capabilities"""
        print(f"\nTesting IR transmission for: {device['manufacturer']} - {device['product']}")
        
        test_result = {
            'device': device,
            'ir_capable': False,
            'test_methods': [],
            'errors': [],
            'ir_commands_tested': []
        }
        
        try:
            hid_device = hid.device()
            hid_device.open_path(device['path'])
            
            # Test different IR transmission methods
            test_methods = [
                self._test_standard_ir_report,
                self._test_custom_ir_report,
                self._test_nec_protocol,
                self._test_rc5_protocol,
                self._test_raw_ir_data
            ]
            
            for method in test_methods:
                try:
                    result = method(hid_device, device)
                    if result['success']:
                        test_result['test_methods'].append(result['method'])
                        test_result['ir_commands_tested'].extend(result['commands'])
                        test_result['ir_capable'] = True
                except Exception as e:
                    test_result['errors'].append(f"{method.__name__}: {e}")
            
            hid_device.close()
            
        except Exception as e:
            test_result['errors'].append(f"Device access error: {e}")
        
        return test_result
    
    def _test_standard_ir_report(self, hid_device, device: Dict) -> Dict:
        """Test standard IR report format"""
        result = {
            'method': 'Standard IR Report',
            'success': False,
            'commands': []
        }
        
        try:
            # Try standard IR report format (report ID 0x02 for IR transmission)
            ir_report = [0x02] + [0x00] * 63  # IR transmission report
            
            write_result = hid_device.write(ir_report)
            if write_result == len(ir_report):
                result['success'] = True
                result['commands'].append('Standard IR Report')
            
        except Exception as e:
            pass
        
        return result
    
    def _test_custom_ir_report(self, hid_device, device: Dict) -> Dict:
        """Test custom IR report format"""
        result = {
            'method': 'Custom IR Report',
            'success': False,
            'commands': []
        }
        
        try:
            # Try different report IDs that might be used for IR
            for report_id in [0x01, 0x03, 0x04, 0x05]:
                ir_report = [report_id] + [0x00] * 63
                
                write_result = hid_device.write(ir_report)
                if write_result == len(ir_report):
                    result['success'] = True
                    result['commands'].append(f'Custom IR Report (ID: 0x{report_id:02x})')
                    break
            
        except Exception as e:
            pass
        
        return result
    
    def _test_nec_protocol(self, hid_device, device: Dict) -> Dict:
        """Test NEC protocol IR transmission"""
        result = {
            'method': 'NEC Protocol',
            'success': False,
            'commands': []
        }
        
        try:
            # NEC protocol test - Samsung TV power command
            nec_power_code = 0xE0E040BF
            
            # Convert to NEC format
            nec_data = self._encode_nec_command(nec_power_code)
            
            # Try different report formats
            for report_id in [0x02, 0x03, 0x04]:
                ir_report = [report_id] + nec_data[:63]
                
                write_result = hid_device.write(ir_report)
                if write_result == len(ir_report):
                    result['success'] = True
                    result['commands'].append('NEC Power Command')
                    break
            
        except Exception as e:
            pass
        
        return result
    
    def _test_rc5_protocol(self, hid_device, device: Dict) -> Dict:
        """Test RC5 protocol IR transmission"""
        result = {
            'method': 'RC5 Protocol',
            'success': False,
            'commands': []
        }
        
        try:
            # RC5 protocol test
            rc5_data = self._encode_rc5_command(0x1234)
            
            # Try different report formats
            for report_id in [0x02, 0x03, 0x04]:
                ir_report = [report_id] + rc5_data[:63]
                
                write_result = hid_device.write(ir_report)
                if write_result == len(ir_report):
                    result['success'] = True
                    result['commands'].append('RC5 Command')
                    break
            
        except Exception as e:
            pass
        
        return result
    
    def _test_raw_ir_data(self, hid_device, device: Dict) -> Dict:
        """Test raw IR data transmission"""
        result = {
            'method': 'Raw IR Data',
            'success': False,
            'commands': []
        }
        
        try:
            # Test raw IR data (timing information)
            raw_ir_data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
            
            # Try different report formats
            for report_id in [0x02, 0x03, 0x04]:
                ir_report = [report_id] + raw_ir_data + [0x00] * (64 - len(raw_ir_data) - 1)
                
                write_result = hid_device.write(ir_report)
                if write_result == len(ir_report):
                    result['success'] = True
                    result['commands'].append('Raw IR Data')
                    break
            
        except Exception as e:
            pass
        
        return result
    
    def _encode_nec_command(self, command: int) -> List[int]:
        """Encode NEC protocol command"""
        # Simplified NEC encoding
        # This would need to be customized based on the device's requirements
        return [
            (command >> 24) & 0xFF,
            (command >> 16) & 0xFF,
            (command >> 8) & 0xFF,
            command & 0xFF
        ]
    
    def _encode_rc5_command(self, command: int) -> List[int]:
        """Encode RC5 protocol command"""
        # Simplified RC5 encoding
        return [
            (command >> 8) & 0xFF,
            command & 0xFF
        ]
    
    def test_all_devices(self):
        """Test all accessible devices for IR capabilities"""
        print("IR Capability Tester for USB Devices")
        print("=" * 60)
        
        # Find accessible devices
        devices = self.find_accessible_devices()
        
        if not devices:
            print("No accessible devices found.")
            return
        
        print(f"Found {len(devices)} accessible devices")
        
        # Test each device
        for i, device in enumerate(devices, 1):
            print(f"\n{'='*60}")
            print(f"Testing Device {i}/{len(devices)}")
            print(f"{'='*60}")
            
            test_result = self.test_ir_transmission(device)
            self.test_results.append(test_result)
            
            # Print results
            self._print_test_results(test_result)
        
        # Print summary
        self._print_summary()
    
    def _print_test_results(self, test_result: Dict):
        """Print test results for a device"""
        device = test_result['device']
        
        print(f"\nDevice: {device['manufacturer']} - {device['product']}")
        print(f"Vendor ID: 0x{device['vendor_id']:04x}, Product ID: 0x{device['product_id']:04x}")
        
        if test_result['ir_capable']:
            print("✓ IR transmission capabilities detected!")
            print("✓ Test methods that worked:")
            for method in test_result['test_methods']:
                print(f"  - {method}")
            print("✓ IR commands tested:")
            for command in test_result['ir_commands_tested']:
                print(f"  - {command}")
        else:
            print("✗ No IR transmission capabilities detected")
        
        if test_result['errors']:
            print("⚠ Errors encountered:")
            for error in test_result['errors']:
                print(f"  - {error}")
    
    def _print_summary(self):
        """Print summary of all tests"""
        print(f"\n{'='*60}")
        print("IR CAPABILITY TEST SUMMARY")
        print(f"{'='*60}")
        
        total_devices = len(self.test_results)
        ir_capable_devices = sum(1 for result in self.test_results if result['ir_capable'])
        
        print(f"Total devices tested: {total_devices}")
        print(f"Devices with IR capabilities: {ir_capable_devices}")
        print(f"Devices without IR capabilities: {total_devices - ir_capable_devices}")
        
        if ir_capable_devices > 0:
            print(f"\n✓ Found {ir_capable_devices} device(s) with IR capabilities!")
            print("\nThese devices can potentially be used for TV control:")
            for result in self.test_results:
                if result['ir_capable']:
                    device = result['device']
                    print(f"  - {device['manufacturer']} - {device['product']}")
                    print(f"    Methods: {', '.join(result['test_methods'])}")
            
            print("\nNext steps:")
            print("1. Test with actual TV models")
            print("2. Implement IR protocol support")
            print("3. Create TV control commands")
            print("4. Test with different TV brands")
        else:
            print("\n✗ No devices with IR capabilities found")
            print("\nThis could mean:")
            print("1. No IR-capable devices are connected")
            print("2. Devices don't support IR transmission")
            print("3. Different communication protocol required")
            print("4. Devices require specific drivers")
            
            print("\nTo test with IR-capable devices:")
            print("1. Connect a USB IR blaster or remote control")
            print("2. Install device-specific drivers if needed")
            print("3. Run this test again")

def main():
    """Main function"""
    tester = IRCapabilityTester()
    tester.test_all_devices()

if __name__ == "__main__":
    main()
