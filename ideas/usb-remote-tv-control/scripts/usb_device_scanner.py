#!/usr/bin/env python3
"""
USB Device Scanner for Remote Control Devices
Scans for USB devices and identifies potential remote control devices
"""

import usb.core
import usb.util
import hid
import sys
import time
from typing import List, Dict, Optional

class USBDeviceScanner:
    """Scanner for USB devices, specifically looking for remote control devices"""
    
    def __init__(self):
        self.devices = []
        self.hid_devices = []
        self.remote_control_candidates = []
    
    def scan_usb_devices(self) -> List[Dict]:
        """Scan for all USB devices"""
        print("Scanning for USB devices...")
        devices = usb.core.find(find_all=True)
        device_list = []
        
        for device in devices:
            try:
                device_info = {
                    'vendor_id': f"0x{device.idVendor:04x}",
                    'product_id': f"0x{device.idProduct:04x}",
                    'vendor_name': self._get_vendor_name(device.idVendor),
                    'product_name': self._get_product_name(device.idVendor, device.idProduct),
                    'device': device
                }
                
                # Try to get configuration details
                try:
                    config = device.get_active_configuration()
                    device_info['configuration'] = config.bConfigurationValue
                    device_info['interfaces'] = []
                    
                    for interface in config:
                        interface_info = {
                            'number': interface.bInterfaceNumber,
                            'class': interface.bInterfaceClass,
                            'subclass': interface.bInterfaceSubClass,
                            'protocol': interface.bInterfaceProtocol,
                            'is_hid': interface.bInterfaceClass == 3  # HID class
                        }
                        device_info['interfaces'].append(interface_info)
                        
                        # Check if this might be a remote control
                        if self._is_remote_control_candidate(interface_info, device_info):
                            device_info['remote_control_candidate'] = True
                            
                except Exception as e:
                    device_info['configuration_error'] = str(e)
                
                device_list.append(device_info)
                self.devices.append(device_info)
                
            except Exception as e:
                print(f"Error accessing device: {e}")
                continue
        
        return device_list
    
    def scan_hid_devices(self) -> List[Dict]:
        """Scan for HID devices specifically"""
        print("\nScanning for HID devices...")
        hid_devices = hid.enumerate()
        hid_device_list = []
        
        for device_info in hid_devices:
            hid_device = {
                'vendor_id': f"0x{device_info['vendor_id']:04x}",
                'product_id': f"0x{device_info['product_id']:04x}",
                'manufacturer': device_info.get('manufacturer_string', 'Unknown'),
                'product': device_info.get('product_string', 'Unknown'),
                'usage_page': device_info.get('usage_page', 0),
                'usage': device_info.get('usage', 0),
                'path': device_info.get('path', ''),
                'interface_number': device_info.get('interface_number', 0),
                'is_remote_control': self._is_hid_remote_control(device_info)
            }
            
            hid_device_list.append(hid_device)
            self.hid_devices.append(hid_device)
            
            if hid_device['is_remote_control']:
                self.remote_control_candidates.append(hid_device)
        
        return hid_device_list
    
    def _get_vendor_name(self, vendor_id: int) -> str:
        """Get vendor name from vendor ID"""
        vendor_names = {
            0x046d: "Logitech Inc.",
            0x05ac: "Apple Inc.",
            0x05e3: "Genesys Logic, Inc.",
            0x1234: "Generic",
            0xabcd: "Generic"
        }
        return vendor_names.get(vendor_id, f"Vendor 0x{vendor_id:04x}")
    
    def _get_product_name(self, vendor_id: int, product_id: int) -> str:
        """Get product name from vendor and product ID"""
        product_names = {
            (0x046d, 0xc077): "USB Optical Mouse",
            (0x05ac, 0x800c): "USB3 Gen2 Hub",
            (0x05ac, 0x800b): "USB2 Hub",
            (0x05e3, 0x0626): "USB3.1 Hub",
            (0x05e3, 0x0749): "USB3.0 Card Reader"
        }
        return product_names.get((vendor_id, product_id), f"Product 0x{product_id:04x}")
    
    def _is_remote_control_candidate(self, interface_info: Dict, device_info: Dict) -> bool:
        """Check if device might be a remote control"""
        # Check for HID interface
        if not interface_info['is_hid']:
            return False
        
        # Check for specific usage pages that might indicate remote control
        # Generic Desktop (0x01) with specific usage codes
        if interface_info['class'] == 3:  # HID class
            # Look for devices that might be remote controls
            vendor_name = device_info['vendor_name'].lower()
            product_name = device_info['product_name'].lower()
            
            remote_keywords = ['remote', 'control', 'ir', 'infrared', 'tv', 'media']
            for keyword in remote_keywords:
                if keyword in vendor_name or keyword in product_name:
                    return True
        
        return False
    
    def _is_hid_remote_control(self, device_info: Dict) -> bool:
        """Check if HID device might be a remote control"""
        usage_page = device_info.get('usage_page', 0)
        usage = device_info.get('usage', 0)
        manufacturer = device_info.get('manufacturer_string', '').lower()
        product = device_info.get('product_string', '').lower()
        
        # Check for remote control specific usage pages
        remote_usage_pages = [0x01, 0x0C]  # Generic Desktop, Consumer
        
        # Check for specific usage codes that might indicate remote control
        remote_usage_codes = [0x06, 0x0C]  # Keyboard, Consumer Control
        
        # Check manufacturer and product names
        remote_keywords = ['remote', 'control', 'ir', 'infrared', 'tv', 'media', 'universal']
        
        is_remote = (
            usage_page in remote_usage_pages or
            usage in remote_usage_codes or
            any(keyword in manufacturer for keyword in remote_keywords) or
            any(keyword in product for keyword in remote_keywords)
        )
        
        return is_remote
    
    def test_device_communication(self, device_info: Dict) -> Dict:
        """Test communication with a specific device"""
        results = {
            'device': device_info,
            'communication_successful': False,
            'capabilities': [],
            'error': None
        }
        
        try:
            if 'path' in device_info:
                # Test HID device
                device = hid.device()
                device.open_path(device_info['path'])
                
                # Try to read device info
                manufacturer = device.get_manufacturer_string()
                product = device.get_product_string()
                serial = device.get_serial_number_string()
                
                results['capabilities'].append('HID Communication')
                results['manufacturer'] = manufacturer
                results['product'] = product
                results['serial'] = serial
                
                # Try to read a report
                try:
                    report = device.read(64, timeout_ms=1000)
                    if report:
                        results['capabilities'].append('Report Reading')
                        results['sample_report'] = list(report[:16])  # First 16 bytes
                except Exception as e:
                    results['capabilities'].append(f'Report Reading Failed: {e}')
                
                device.close()
                results['communication_successful'] = True
                
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def print_scan_results(self):
        """Print comprehensive scan results"""
        print("\n" + "="*80)
        print("USB DEVICE SCAN RESULTS")
        print("="*80)
        
        print(f"\nTotal USB devices found: {len(self.devices)}")
        print(f"Total HID devices found: {len(self.hid_devices)}")
        print(f"Remote control candidates: {len(self.remote_control_candidates)}")
        
        if self.remote_control_candidates:
            print("\n" + "-"*60)
            print("REMOTE CONTROL CANDIDATES:")
            print("-"*60)
            
            for i, device in enumerate(self.remote_control_candidates, 1):
                print(f"\n{i}. {device['manufacturer']} - {device['product']}")
                print(f"   Vendor ID: {device['vendor_id']}")
                print(f"   Product ID: {device['product_id']}")
                print(f"   Usage Page: 0x{device['usage_page']:02x}")
                print(f"   Usage: 0x{device['usage']:02x}")
                print(f"   Interface: {device['interface_number']}")
                
                # Test communication
                print("   Testing communication...")
                test_result = self.test_device_communication(device)
                
                if test_result['communication_successful']:
                    print("   ✓ Communication successful")
                    if test_result['capabilities']:
                        print(f"   Capabilities: {', '.join(test_result['capabilities'])}")
                    if 'sample_report' in test_result:
                        print(f"   Sample report: {test_result['sample_report']}")
                else:
                    print(f"   ✗ Communication failed: {test_result['error']}")
        
        print("\n" + "-"*60)
        print("ALL HID DEVICES:")
        print("-"*60)
        
        for i, device in enumerate(self.hid_devices, 1):
            print(f"\n{i}. {device['manufacturer']} - {device['product']}")
            print(f"   Vendor ID: {device['vendor_id']}")
            print(f"   Product ID: {device['product_id']}")
            print(f"   Usage Page: 0x{device['usage_page']:02x}")
            print(f"   Usage: 0x{device['usage']:02x}")
            print(f"   Remote Control: {'Yes' if device['is_remote_control'] else 'No'}")

def main():
    """Main function to run USB device scan"""
    print("USB Remote Control Device Scanner")
    print("="*50)
    
    scanner = USBDeviceScanner()
    
    # Scan USB devices
    usb_devices = scanner.scan_usb_devices()
    
    # Scan HID devices
    hid_devices = scanner.scan_hid_devices()
    
    # Print results
    scanner.print_scan_results()
    
    # Additional analysis
    print("\n" + "="*80)
    print("ANALYSIS AND RECOMMENDATIONS")
    print("="*80)
    
    if scanner.remote_control_candidates:
        print("\n✓ Found potential remote control devices!")
        print("These devices may be capable of IR transmission or remote control functions.")
        print("\nNext steps:")
        print("1. Test IR signal transmission capabilities")
        print("2. Analyze HID report structure")
        print("3. Test with actual TV models")
        print("4. Implement IR protocol support")
    else:
        print("\n✗ No obvious remote control devices found.")
        print("\nThis could mean:")
        print("1. No remote control device is currently connected")
        print("2. The device is not recognized as a remote control")
        print("3. The device uses a different interface (not HID)")
        print("4. The device requires specific drivers")
        
        print("\nTo test with a remote control device:")
        print("1. Connect a USB remote control device")
        print("2. Run this scanner again")
        print("3. Look for devices with IR or remote control capabilities")

if __name__ == "__main__":
    main()
