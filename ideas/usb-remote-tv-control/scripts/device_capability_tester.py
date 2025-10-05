#!/usr/bin/env python3
"""
Device Capability Tester for USB Remote Control Devices
Tests the capabilities of connected HID devices for remote control functions
"""

import hid
import time
import json
from typing import Dict, List, Optional

class DeviceCapabilityTester:
    """Test capabilities of HID devices for remote control functions"""
    
    def __init__(self):
        self.devices = []
        self.test_results = []
    
    def find_remote_control_devices(self) -> List[Dict]:
        """Find devices that might be remote controls"""
        print("Scanning for remote control capable devices...")
        
        all_devices = hid.enumerate()
        remote_devices = []
        
        for device_info in all_devices:
            # Check if device might be a remote control
            if self._is_remote_control_candidate(device_info):
                device = {
                    'vendor_id': device_info['vendor_id'],
                    'product_id': device_info['product_id'],
                    'manufacturer': device_info.get('manufacturer_string', 'Unknown'),
                    'product': device_info.get('product_string', 'Unknown'),
                    'usage_page': device_info.get('usage_page', 0),
                    'usage': device_info.get('usage', 0),
                    'path': device_info.get('path', ''),
                    'interface_number': device_info.get('interface_number', 0),
                    'device_info': device_info
                }
                remote_devices.append(device)
        
        return remote_devices
    
    def _is_remote_control_candidate(self, device_info: Dict) -> bool:
        """Check if device might be a remote control"""
        usage_page = device_info.get('usage_page', 0)
        usage = device_info.get('usage', 0)
        manufacturer = device_info.get('manufacturer_string', '').lower()
        product = device_info.get('product_string', '').lower()
        
        # Check for remote control specific usage pages
        remote_usage_pages = [0x01, 0x0C]  # Generic Desktop, Consumer
        
        # Check for specific usage codes that might indicate remote control
        remote_usage_codes = [0x06, 0x0C, 0x01, 0x02]  # Keyboard, Consumer Control, Pointer, Mouse
        
        # Check manufacturer and product names
        remote_keywords = ['remote', 'control', 'ir', 'infrared', 'tv', 'media', 'universal']
        
        is_remote = (
            usage_page in remote_usage_pages or
            usage in remote_usage_codes or
            any(keyword in manufacturer for keyword in remote_keywords) or
            any(keyword in product for keyword in remote_keywords)
        )
        
        return is_remote
    
    def test_device_capabilities(self, device: Dict) -> Dict:
        """Test capabilities of a specific device"""
        print(f"\nTesting device: {device['manufacturer']} - {device['product']}")
        print(f"Vendor ID: 0x{device['vendor_id']:04x}, Product ID: 0x{device['product_id']:04x}")
        
        test_result = {
            'device': device,
            'connection_successful': False,
            'capabilities': [],
            'errors': [],
            'sample_data': [],
            'report_analysis': {}
        }
        
        try:
            # Open device
            hid_device = hid.device()
            hid_device.open_path(device['path'])
            test_result['connection_successful'] = True
            test_result['capabilities'].append('HID Connection')
            
            # Get device information
            try:
                manufacturer = hid_device.get_manufacturer_string()
                product = hid_device.get_product_string()
                serial = hid_device.get_serial_number_string()
                
                test_result['device_info'] = {
                    'manufacturer': manufacturer,
                    'product': product,
                    'serial': serial
                }
                test_result['capabilities'].append('Device Info Access')
                
            except Exception as e:
                test_result['errors'].append(f'Device info error: {e}')
            
            # Test report reading
            try:
                print("  Testing report reading...")
                reports_read = 0
                sample_reports = []
                
                # Try to read multiple reports
                for i in range(5):
                    try:
                        report = hid_device.read(64, timeout_ms=1000)
                        if report:
                            reports_read += 1
                            sample_reports.append(list(report))
                            test_result['sample_data'].append({
                                'report_number': i + 1,
                                'data': list(report),
                                'timestamp': time.time()
                            })
                    except Exception as e:
                        if i == 0:  # Only report first error
                            test_result['errors'].append(f'Report reading error: {e}')
                        break
                
                if reports_read > 0:
                    test_result['capabilities'].append(f'Report Reading ({reports_read} reports)')
                    test_result['sample_data'] = sample_reports
                    
                    # Analyze reports
                    analysis = self._analyze_reports(sample_reports)
                    test_result['report_analysis'] = analysis
                    
            except Exception as e:
                test_result['errors'].append(f'Report reading failed: {e}')
            
            # Test report writing (if device supports it)
            try:
                print("  Testing report writing...")
                # Try to write a test report
                test_report = [0x01] + [0x00] * 63  # Simple test report
                result = hid_device.write(test_report)
                
                if result == len(test_report):
                    test_result['capabilities'].append('Report Writing')
                else:
                    test_result['errors'].append(f'Report writing failed: wrote {result} bytes')
                    
            except Exception as e:
                test_result['errors'].append(f'Report writing error: {e}')
            
            # Test IR signal capabilities (if applicable)
            try:
                print("  Testing IR signal capabilities...")
                ir_capabilities = self._test_ir_capabilities(hid_device)
                if ir_capabilities:
                    test_result['capabilities'].extend(ir_capabilities)
                    
            except Exception as e:
                test_result['errors'].append(f'IR testing error: {e}')
            
            hid_device.close()
            
        except Exception as e:
            test_result['errors'].append(f'Device connection failed: {e}')
        
        return test_result
    
    def _analyze_reports(self, reports: List[List[int]]) -> Dict:
        """Analyze HID reports to understand device capabilities"""
        analysis = {
            'report_count': len(reports),
            'report_size': len(reports[0]) if reports else 0,
            'data_patterns': {},
            'button_states': [],
            'ir_signals': [],
            'capabilities_detected': []
        }
        
        if not reports:
            return analysis
        
        # Analyze data patterns
        for i, report in enumerate(reports):
            # Look for button states (non-zero values in specific positions)
            button_data = [b for b in report[1:9] if b != 0]  # Skip report ID
            if button_data:
                analysis['button_states'].append({
                    'report': i,
                    'buttons': button_data
                })
            
            # Look for IR signal patterns (specific byte patterns)
            if self._detect_ir_pattern(report):
                analysis['ir_signals'].append({
                    'report': i,
                    'data': report
                })
        
        # Detect capabilities
        if analysis['button_states']:
            analysis['capabilities_detected'].append('Button Input')
        
        if analysis['ir_signals']:
            analysis['capabilities_detected'].append('IR Signal Output')
        
        # Check for specific usage patterns
        if any(report[0] == 0x01 for report in reports):
            analysis['capabilities_detected'].append('Standard HID Report')
        
        return analysis
    
    def _detect_ir_pattern(self, report: List[int]) -> bool:
        """Detect if report might contain IR signal data"""
        # Look for patterns that might indicate IR signals
        # This is a simplified detection - actual implementation would need
        # to understand the specific device's IR signal format
        
        # Check for non-zero data in positions that might contain IR signals
        if len(report) > 8:
            # Look for data in positions that might be IR signals
            ir_positions = report[8:16]  # Positions 8-15 might contain IR data
            if any(b != 0 for b in ir_positions):
                return True
        
        return False
    
    def _test_ir_capabilities(self, hid_device) -> List[str]:
        """Test IR signal capabilities of the device"""
        capabilities = []
        
        try:
            # Try to send a test IR signal
            # This would need to be customized based on the device's IR protocol
            test_ir_report = [0x02] + [0x00] * 63  # IR transmission report
            
            result = hid_device.write(test_ir_report)
            if result == len(test_ir_report):
                capabilities.append('IR Signal Transmission')
            
            # Try to read IR feedback
            try:
                feedback = hid_device.read(64, timeout_ms=100)
                if feedback and any(b != 0 for b in feedback):
                    capabilities.append('IR Signal Feedback')
            except:
                pass
                
        except Exception as e:
            pass
        
        return capabilities
    
    def test_all_devices(self):
        """Test all remote control capable devices"""
        print("USB Remote Control Device Capability Tester")
        print("=" * 60)
        
        # Find devices
        devices = self.find_remote_control_devices()
        
        if not devices:
            print("No remote control capable devices found.")
            return
        
        print(f"Found {len(devices)} potential remote control devices")
        
        # Test each device
        for i, device in enumerate(devices, 1):
            print(f"\n{'='*60}")
            print(f"Testing Device {i}/{len(devices)}")
            print(f"{'='*60}")
            
            test_result = self.test_device_capabilities(device)
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
        
        if test_result['connection_successful']:
            print("✓ Connection successful")
            
            if test_result['capabilities']:
                print("✓ Capabilities:")
                for capability in test_result['capabilities']:
                    print(f"  - {capability}")
            
            if test_result['errors']:
                print("⚠ Errors:")
                for error in test_result['errors']:
                    print(f"  - {error}")
            
            if test_result['sample_data']:
                print(f"✓ Sample data collected: {len(test_result['sample_data'])} reports")
                
            if test_result['report_analysis']:
                analysis = test_result['report_analysis']
                print(f"✓ Report analysis:")
                print(f"  - Report count: {analysis['report_count']}")
                print(f"  - Report size: {analysis['report_size']} bytes")
                if analysis['capabilities_detected']:
                    print(f"  - Detected capabilities: {', '.join(analysis['capabilities_detected'])}")
        else:
            print("✗ Connection failed")
            if test_result['errors']:
                for error in test_result['errors']:
                    print(f"  - {error}")
    
    def _print_summary(self):
        """Print summary of all tests"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        
        successful_connections = sum(1 for result in self.test_results if result['connection_successful'])
        total_devices = len(self.test_results)
        
        print(f"Total devices tested: {total_devices}")
        print(f"Successful connections: {successful_connections}")
        print(f"Failed connections: {total_devices - successful_connections}")
        
        # Find devices with IR capabilities
        ir_devices = []
        for result in self.test_results:
            if result['connection_successful']:
                capabilities = result['capabilities']
                if any('IR' in cap for cap in capabilities):
                    ir_devices.append(result['device'])
        
        if ir_devices:
            print(f"\n✓ Devices with IR capabilities: {len(ir_devices)}")
            for device in ir_devices:
                print(f"  - {device['manufacturer']} - {device['product']}")
        else:
            print("\n✗ No devices with confirmed IR capabilities found")
        
        # Recommendations
        print(f"\n{'='*60}")
        print("RECOMMENDATIONS")
        print(f"{'='*60}")
        
        if successful_connections > 0:
            print("✓ Some devices are accessible and can be tested further")
            print("\nNext steps:")
            print("1. Test IR signal transmission with actual TV models")
            print("2. Analyze HID report structure for IR commands")
            print("3. Implement IR protocol support")
            print("4. Test with different TV brands and models")
        else:
            print("✗ No devices could be accessed")
            print("\nPossible issues:")
            print("1. Device drivers not installed")
            print("2. Permission issues with USB device access")
            print("3. Devices not compatible with HID interface")
            print("4. Devices require specific drivers")

def main():
    """Main function"""
    tester = DeviceCapabilityTester()
    tester.test_all_devices()

if __name__ == "__main__":
    main()
