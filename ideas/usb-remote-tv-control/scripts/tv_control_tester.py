#!/usr/bin/env python3
"""
TV Control Tester
Tests actual TV control using USB devices with IR capabilities
"""

import hid
import time
import struct
from typing import Dict, List, Optional

class TVControlTester:
    """Test TV control using USB devices with IR capabilities"""
    
    def __init__(self):
        self.ir_devices = []
        self.tv_codes = {
            'samsung': {
                'power': 0xE0E040BF,
                'volume_up': 0xE0E0E01F,
                'volume_down': 0xE0E0D02F,
                'channel_up': 0xE0E048B7,
                'channel_down': 0xE0E008F7,
                'mute': 0xE0E0F00F,
                'input_hdmi1': 0xE0E0D12E,
                'input_hdmi2': 0xE0E0D22D,
                'menu': 0xE0E058A7,
                'back': 0xE0E01AE5,
                'home': 0xE0E09E61,
                'up': 0xE0E006F9,
                'down': 0xE0E08679,
                'left': 0xE0E0A659,
                'right': 0xE0E046B9,
                'ok': 0xE0E016E9
            },
            'lg': {
                'power': 0x20DF10EF,
                'volume_up': 0x20DF40BF,
                'volume_down': 0x20DFC03F,
                'channel_up': 0x20DF00FF,
                'channel_down': 0x20DF807F,
                'mute': 0x20DF906F,
                'input_hdmi1': 0x20DFD02F,
                'input_hdmi2': 0x20DFD12E,
                'menu': 0x20DF22DD,
                'back': 0x20DF14EB,
                'home': 0x20DF8E71,
                'up': 0x20DF02FD,
                'down': 0x20DF827D,
                'left': 0x20DFE01F,
                'right': 0x20DF609F,
                'ok': 0x20DF22DD
            },
            'sony': {
                'power': 0xA90,
                'volume_up': 0x490,
                'volume_down': 0xC90,
                'channel_up': 0x90,
                'channel_down': 0x890,
                'mute': 0x290,
                'input_hdmi1': 0x1D0,
                'input_hdmi2': 0x1D1,
                'menu': 0x1A0,
                'back': 0x1A1,
                'home': 0x1A2,
                'up': 0x1A3,
                'down': 0x1A4,
                'left': 0x1A5,
                'right': 0x1A6,
                'ok': 0x1A7
            }
        }
    
    def find_ir_capable_devices(self) -> List[Dict]:
        """Find devices with IR capabilities"""
        print("Finding IR-capable devices...")
        
        all_devices = hid.enumerate()
        ir_devices = []
        
        for device_info in all_devices:
            try:
                # Try to open device
                device = hid.device()
                device.open_path(device_info['path'])
                
                # Get device info
                manufacturer = device.get_manufacturer_string()
                product = device.get_product_string()
                
                # Test IR capability
                if self._test_ir_capability(device):
                    device_data = {
                        'vendor_id': device_info['vendor_id'],
                        'product_id': device_info['product_id'],
                        'manufacturer': manufacturer,
                        'product': product,
                        'path': device_info['path'],
                        'interface_number': device_info.get('interface_number', 0),
                        'device_info': device_info
                    }
                    ir_devices.append(device_data)
                
                device.close()
                
            except Exception as e:
                continue
        
        return ir_devices
    
    def _test_ir_capability(self, device) -> bool:
        """Test if device has IR capabilities"""
        try:
            # Try to send a simple IR report
            ir_report = [0x02] + [0x00] * 63
            result = device.write(ir_report)
            return result == len(ir_report)
        except:
            return False
    
    def send_tv_command(self, device: Dict, tv_brand: str, command: str) -> bool:
        """Send TV command using IR device"""
        try:
            # Get IR code for command
            if tv_brand not in self.tv_codes:
                print(f"Unsupported TV brand: {tv_brand}")
                return False
            
            if command not in self.tv_codes[tv_brand]:
                print(f"Unsupported command: {command}")
                return False
            
            ir_code = self.tv_codes[tv_brand][command]
            
            # Open device
            hid_device = hid.device()
            hid_device.open_path(device['path'])
            
            # Send IR command
            success = self._send_ir_command(hid_device, ir_code, tv_brand)
            
            hid_device.close()
            return success
            
        except Exception as e:
            print(f"Error sending TV command: {e}")
            return False
    
    def _send_ir_command(self, hid_device, ir_code: int, tv_brand: str) -> bool:
        """Send IR command to device"""
        try:
            if tv_brand == 'samsung':
                return self._send_nec_command(hid_device, ir_code)
            elif tv_brand == 'lg':
                return self._send_nec_command(hid_device, ir_code)
            elif tv_brand == 'sony':
                return self._send_sony_command(hid_device, ir_code)
            else:
                return self._send_nec_command(hid_device, ir_code)
        except Exception as e:
            print(f"Error sending IR command: {e}")
            return False
    
    def _send_nec_command(self, hid_device, ir_code: int) -> bool:
        """Send NEC protocol command"""
        try:
            # NEC protocol format
            nec_data = [
                (ir_code >> 24) & 0xFF,
                (ir_code >> 16) & 0xFF,
                (ir_code >> 8) & 0xFF,
                ir_code & 0xFF
            ]
            
            # Try different report formats
            for report_id in [0x02, 0x03, 0x04]:
                ir_report = [report_id] + nec_data + [0x00] * (64 - len(nec_data) - 1)
                
                result = hid_device.write(ir_report)
                if result == len(ir_report):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error sending NEC command: {e}")
            return False
    
    def _send_sony_command(self, hid_device, ir_code: int) -> bool:
        """Send Sony protocol command"""
        try:
            # Sony protocol format
            sony_data = [
                (ir_code >> 8) & 0xFF,
                ir_code & 0xFF
            ]
            
            # Try different report formats
            for report_id in [0x02, 0x03, 0x04]:
                ir_report = [report_id] + sony_data + [0x00] * (64 - len(sony_data) - 1)
                
                result = hid_device.write(ir_report)
                if result == len(ir_report):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error sending Sony command: {e}")
            return False
    
    def test_tv_control(self):
        """Test TV control with available devices"""
        print("TV Control Tester")
        print("=" * 60)
        
        # Find IR-capable devices
        devices = self.find_ir_capable_devices()
        
        if not devices:
            print("No IR-capable devices found.")
            return
        
        print(f"Found {len(devices)} IR-capable devices")
        
        # Test each device
        for i, device in enumerate(devices, 1):
            print(f"\n{'='*60}")
            print(f"Testing Device {i}/{len(devices)}")
            print(f"{'='*60}")
            
            print(f"Device: {device['manufacturer']} - {device['product']}")
            print(f"Vendor ID: 0x{device['vendor_id']:04x}, Product ID: 0x{device['product_id']:04x}")
            
            # Test basic commands
            self._test_basic_commands(device)
            
            # Test TV-specific commands
            self._test_tv_commands(device)
    
    def _test_basic_commands(self, device: Dict):
        """Test basic TV commands"""
        print("\nTesting basic TV commands...")
        
        # Test with Samsung TV codes
        test_commands = ['power', 'volume_up', 'volume_down', 'mute']
        
        for command in test_commands:
            print(f"  Testing {command}...")
            success = self.send_tv_command(device, 'samsung', command)
            if success:
                print(f"    ✓ {command} command sent successfully")
            else:
                print(f"    ✗ {command} command failed")
            
            # Wait between commands
            time.sleep(0.5)
    
    def _test_tv_commands(self, device: Dict):
        """Test TV-specific commands"""
        print("\nTesting TV-specific commands...")
        
        # Test with different TV brands
        tv_brands = ['samsung', 'lg', 'sony']
        
        for brand in tv_brands:
            print(f"\n  Testing {brand.upper()} TV commands...")
            
            # Test power command
            print(f"    Testing {brand} power command...")
            success = self.send_tv_command(device, brand, 'power')
            if success:
                print(f"      ✓ {brand} power command sent")
            else:
                print(f"      ✗ {brand} power command failed")
            
            # Wait between brands
            time.sleep(1)
    
    def interactive_test(self):
        """Interactive TV control test"""
        print("\nInteractive TV Control Test")
        print("=" * 60)
        
        # Find IR-capable devices
        devices = self.find_ir_capable_devices()
        
        if not devices:
            print("No IR-capable devices found.")
            return
        
        print(f"Found {len(devices)} IR-capable devices")
        
        # Let user select device
        print("\nAvailable devices:")
        for i, device in enumerate(devices, 1):
            print(f"{i}. {device['manufacturer']} - {device['product']}")
        
        try:
            choice = int(input("\nSelect device (1-{}): ".format(len(devices))))
            if 1 <= choice <= len(devices):
                selected_device = devices[choice - 1]
                print(f"Selected: {selected_device['manufacturer']} - {selected_device['product']}")
                
                # Let user select TV brand
                print("\nAvailable TV brands:")
                for i, brand in enumerate(self.tv_codes.keys(), 1):
                    print(f"{i}. {brand.upper()}")
                
                tv_choice = int(input("\nSelect TV brand (1-{}): ".format(len(self.tv_codes))))
                tv_brands = list(self.tv_codes.keys())
                if 1 <= tv_choice <= len(tv_brands):
                    selected_tv = tv_brands[tv_choice - 1]
                    print(f"Selected: {selected_tv.upper()}")
                    
                    # Interactive command testing
                    self._interactive_command_test(selected_device, selected_tv)
                else:
                    print("Invalid TV brand selection")
            else:
                print("Invalid device selection")
        except ValueError:
            print("Invalid input")
    
    def _interactive_command_test(self, device: Dict, tv_brand: str):
        """Interactive command testing"""
        print(f"\nInteractive testing with {device['manufacturer']} - {device['product']}")
        print(f"TV brand: {tv_brand.upper()}")
        print("\nAvailable commands:")
        
        commands = list(self.tv_codes[tv_brand].keys())
        for i, command in enumerate(commands, 1):
            print(f"{i}. {command}")
        
        print("\nEnter command number (0 to exit):")
        
        while True:
            try:
                choice = int(input("Command: "))
                if choice == 0:
                    break
                elif 1 <= choice <= len(commands):
                    command = commands[choice - 1]
                    print(f"Sending {command} command...")
                    
                    success = self.send_tv_command(device, tv_brand, command)
                    if success:
                        print(f"✓ {command} command sent successfully")
                    else:
                        print(f"✗ {command} command failed")
                else:
                    print("Invalid command number")
            except ValueError:
                print("Invalid input")
            except KeyboardInterrupt:
                print("\nExiting...")
                break

def main():
    """Main function"""
    tester = TVControlTester()
    
    print("TV Control Tester")
    print("=" * 60)
    print("1. Run automatic tests")
    print("2. Interactive testing")
    
    try:
        choice = int(input("\nSelect option (1-2): "))
        if choice == 1:
            tester.test_tv_control()
        elif choice == 2:
            tester.interactive_test()
        else:
            print("Invalid option")
    except ValueError:
        print("Invalid input")
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
