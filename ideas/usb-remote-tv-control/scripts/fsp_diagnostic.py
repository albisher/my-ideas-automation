#!/usr/bin/env python3
"""
FSP Device Diagnostic Tool
Comprehensive diagnostic for FSP2C01915A chip detection
"""

import usb.core
import usb.util
import hid
import time
import subprocess
import sys

def run_fsp_diagnostic():
    """Run comprehensive FSP device diagnostic"""
    
    print("FSP2C01915A Device Diagnostic Tool")
    print("=" * 60)
    
    # Method 1: Standard USB enumeration
    print("\n1. Standard USB Device Enumeration")
    print("-" * 40)
    
    devices = usb.core.find(find_all=True)
    device_count = 0
    
    for device in devices:
        device_count += 1
        try:
            print(f"Device {device_count}:")
            print(f"  Vendor ID: 0x{device.idVendor:04x}")
            print(f"  Product ID: 0x{device.idProduct:04x}")
            print(f"  Device Class: {device.bDeviceClass}")
            print(f"  Device Subclass: {device.bDeviceSubClass}")
            print(f"  Device Protocol: {device.bDeviceProtocol}")
            
            # Check for FSP characteristics
            if (device.idVendor == 0x1234 or device.idVendor == 0xabcd or
                device.idVendor >= 0x1000 or device.idProduct >= 0x1000):
                print("  *** POTENTIAL FSP DEVICE ***")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"\nTotal USB devices found: {device_count}")
    
    # Method 2: HID device enumeration
    print("\n2. HID Device Enumeration")
    print("-" * 40)
    
    hid_devices = hid.enumerate()
    hid_count = 0
    fsp_candidates = []
    
    for device_info in hid_devices:
        hid_count += 1
        vendor_id = device_info['vendor_id']
        product_id = device_info['product_id']
        manufacturer = device_info.get('manufacturer_string', '')
        product = device_info.get('product_string', '')
        
        print(f"HID Device {hid_count}:")
        print(f"  Vendor ID: 0x{vendor_id:04x}")
        print(f"  Product ID: 0x{product_id:04x}")
        print(f"  Manufacturer: {manufacturer}")
        print(f"  Product: {product}")
        print(f"  Usage Page: 0x{device_info.get('usage_page', 0):02x}")
        print(f"  Usage: 0x{device_info.get('usage', 0):02x}")
        
        # Check for FSP characteristics
        fsp_keywords = ['fsp', 'remote', 'control', 'ir', 'infrared', 'tv', 'universal', 'blaster']
        is_fsp_candidate = any(keyword in manufacturer.lower() or keyword in product.lower() 
                             for keyword in fsp_keywords)
        
        if is_fsp_candidate:
            print("  *** FSP CANDIDATE ***")
            fsp_candidates.append(device_info)
    
    print(f"\nTotal HID devices found: {hid_count}")
    print(f"FSP candidates: {len(fsp_candidates)}")
    
    # Method 3: Test FSP candidates
    if fsp_candidates:
        print("\n3. Testing FSP Candidates")
        print("-" * 40)
        
        for i, device_info in enumerate(fsp_candidates, 1):
            print(f"\nTesting FSP Candidate {i}:")
            print(f"  {device_info.get('manufacturer_string', 'Unknown')} - {device_info.get('product_string', 'Unknown')}")
            
            try:
                device = hid.device()
                device.open_path(device_info['path'])
                print("  ✓ Device opened successfully")
                
                # Test IR capabilities
                test_reports = [
                    ([0x01] + [0x00] * 63, 'Standard Report'),
                    ([0x02] + [0x00] * 63, 'IR Report'),
                    ([0x03] + [0x00] * 63, 'Custom Report 1'),
                    ([0x04] + [0x00] * 63, 'Custom Report 2'),
                ]
                
                ir_success = False
                for report, description in test_reports:
                    try:
                        result = device.write(report)
                        if result == len(report):
                            print(f"    ✓ {description}: Success")
                            ir_success = True
                        else:
                            print(f"    ✗ {description}: Failed")
                    except Exception as e:
                        print(f"    ✗ {description}: Error - {e}")
                
                if ir_success:
                    print("  *** FSP DEVICE WITH IR CAPABILITIES CONFIRMED! ***")
                
                device.close()
                
            except Exception as e:
                print(f"  ✗ Device access failed: {e}")
    
    # Method 4: System USB information
    print("\n4. System USB Information")
    print("-" * 40)
    
    try:
        result = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            usb_info = result.stdout
            
            # Look for FSP-related information
            lines = usb_info.split('\n')
            fsp_lines = []
            
            for line in lines:
                if any(keyword in line.lower() for keyword in 
                      ['fsp', 'remote', 'control', 'ir', 'infrared', 'tv', 'universal']):
                    fsp_lines.append(line.strip())
            
            if fsp_lines:
                print("FSP-related information found:")
                for line in fsp_lines:
                    print(f"  {line}")
            else:
                print("No FSP-related information found in system USB data")
                
        else:
            print("Could not retrieve system USB information")
            
    except Exception as e:
        print(f"Error getting system USB info: {e}")
    
    # Method 5: Recommendations
    print("\n5. Diagnostic Recommendations")
    print("-" * 40)
    
    if not fsp_candidates:
        print("❌ No FSP devices detected")
        print("\nPossible reasons:")
        print("1. FSP device not connected to USB")
        print("2. FSP device not powered on")
        print("3. FSP device using different USB port")
        print("4. FSP device requires specific drivers")
        print("5. FSP device using non-HID protocol")
        print("6. FSP device not properly enumerated")
        
        print("\nTroubleshooting steps:")
        print("1. Check physical USB connection")
        print("2. Try different USB port")
        print("3. Check if device requires external power")
        print("4. Install device-specific drivers")
        print("5. Check device documentation for setup requirements")
        
    else:
        print("✓ FSP candidates found")
        print(f"Found {len(fsp_candidates)} potential FSP devices")
        
        for i, device_info in enumerate(fsp_candidates, 1):
            print(f"{i}. {device_info.get('manufacturer_string', 'Unknown')} - {device_info.get('product_string', 'Unknown')}")
    
    print("\n" + "=" * 60)
    print("FSP Diagnostic Complete")

if __name__ == "__main__":
    run_fsp_diagnostic()
