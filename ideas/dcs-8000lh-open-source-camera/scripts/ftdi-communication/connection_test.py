#!/usr/bin/env python3
"""
FTDI Connection Test for DCS-8000LH Camera
Test FTDI USB connection and communication with the camera.
"""

import serial
import time
import sys
import argparse
import logging
from typing import Optional, List
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for cross-platform colored output
colorama.init()

class ConnectionTester:
    """Test FTDI USB connection with DCS-8000LH camera."""
    
    def __init__(self, port: str, baud: int = 115200, timeout: float = 1.0):
        """Initialize connection tester.
        
        Args:
            port: Serial port (e.g., 'COM3', '/dev/ttyUSB0')
            baud: Baud rate (default: 115200)
            timeout: Timeout in seconds (default: 1.0)
        """
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self.connected = False
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('ConnectionTester')
        logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
        
    def connect(self) -> bool:
        """Connect to serial port.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            if self.ser.is_open:
                self.connected = True
                self.logger.info(f"Connected to {self.port} at {self.baud} baud")
                return True
            else:
                self.logger.error(f"Failed to open {self.port}")
                return False
                
        except serial.SerialException as e:
            self.logger.error(f"Serial error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from serial port."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.connected = False
            self.logger.info("Disconnected from serial port")
    
    def test_basic_connection(self) -> bool:
        """Test basic serial connection.
        
        Returns:
            True if successful, False otherwise
        """
        print(f"{Fore.CYAN}Testing basic serial connection...{Style.RESET_ALL}")
        
        if not self.connected:
            print(f"{Fore.RED}Not connected to serial port{Style.RESET_ALL}")
            return False
        
        try:
            # Test if we can read from port
            if self.ser.in_waiting > 0:
                data = self.ser.read(self.ser.in_waiting)
                print(f"{Fore.GREEN}Received data: {data}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.YELLOW}No data available on port{Style.RESET_ALL}")
                return True
                
        except Exception as e:
            print(f"{Fore.RED}Error testing basic connection: {e}{Style.RESET_ALL}")
            return False
    
    def test_loopback(self) -> bool:
        """Test loopback connection (if available).
        
        Returns:
            True if successful, False otherwise
        """
        print(f"{Fore.CYAN}Testing loopback connection...{Style.RESET_ALL}")
        
        if not self.connected:
            print(f"{Fore.RED}Not connected to serial port{Style.RESET_ALL}")
            return False
        
        try:
            # Send test data
            test_data = b"TEST_LOOPBACK\r\n"
            self.ser.write(test_data)
            time.sleep(0.1)
            
            # Try to read response
            response = self.ser.read(100)
            if response:
                print(f"{Fore.GREEN}Loopback test successful: {response}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.YELLOW}No loopback response (this is normal for camera){Style.RESET_ALL}")
                return True
                
        except Exception as e:
            print(f"{Fore.RED}Error testing loopback: {e}{Style.RESET_ALL}")
            return False
    
    def test_camera_boot(self) -> bool:
        """Test camera boot sequence detection.
        
        Returns:
            True if successful, False otherwise
        """
        print(f"{Fore.CYAN}Testing camera boot sequence...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please power cycle the camera now{Style.RESET_ALL}")
        
        if not self.connected:
            print(f"{Fore.RED}Not connected to serial port{Style.RESET_ALL}")
            return False
        
        try:
            # Clear input buffer
            self.ser.reset_input_buffer()
            
            # Wait for boot messages
            print(f"{Fore.YELLOW}Waiting for boot messages (30 seconds)...{Style.RESET_ALL}")
            
            start_time = time.time()
            boot_messages = []
            
            while time.time() - start_time < 30.0:
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    message = data.decode('utf-8', errors='ignore')
                    boot_messages.append(message)
                    print(f"{Fore.WHITE}{message}{Style.RESET_ALL}", end='')
                
                time.sleep(0.01)
            
            if boot_messages:
                print(f"\n{Fore.GREEN}Boot messages detected{Style.RESET_ALL}")
                return True
            else:
                print(f"\n{Fore.RED}No boot messages detected{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}Error testing camera boot: {e}{Style.RESET_ALL}")
            return False
    
    def test_uboot_prompt(self) -> bool:
        """Test U-Boot prompt detection.
        
        Returns:
            True if successful, False otherwise
        """
        print(f"{Fore.CYAN}Testing U-Boot prompt detection...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press any key during boot to access U-Boot{Style.RESET_ALL}")
        
        if not self.connected:
            print(f"{Fore.RED}Not connected to serial port{Style.RESET_ALL}")
            return False
        
        try:
            # Wait for U-Boot prompt
            print(f"{Fore.YELLOW}Waiting for U-Boot prompt (30 seconds)...{Style.RESET_ALL}")
            
            start_time = time.time()
            buffer = ""
            
            while time.time() - start_time < 30.0:
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    buffer += data.decode('utf-8', errors='ignore')
                    
                    if "=>" in buffer or "U-Boot" in buffer:
                        print(f"\n{Fore.GREEN}U-Boot prompt detected{Style.RESET_ALL}")
                        return True
                    
                    # Keep only last 1000 characters
                    if len(buffer) > 1000:
                        buffer = buffer[-1000:]
                
                time.sleep(0.01)
            
            print(f"\n{Fore.RED}U-Boot prompt not detected{Style.RESET_ALL}")
            return False
            
        except Exception as e:
            print(f"{Fore.RED}Error testing U-Boot prompt: {e}{Style.RESET_ALL}")
            return False
    
    def test_command_execution(self) -> bool:
        """Test command execution via serial.
        
        Returns:
            True if successful, False otherwise
        """
        print(f"{Fore.CYAN}Testing command execution...{Style.RESET_ALL}")
        
        if not self.connected:
            print(f"{Fore.RED}Not connected to serial port{Style.RESET_ALL}")
            return False
        
        try:
            # Send help command
            help_cmd = "help\r\n"
            self.ser.write(help_cmd.encode())
            time.sleep(1.0)
            
            # Read response
            response = self.ser.read(1000)
            if response:
                print(f"{Fore.GREEN}Command execution successful{Style.RESET_ALL}")
                print(f"{Fore.WHITE}{response.decode('utf-8', errors='ignore')}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}No response to command{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}Error testing command execution: {e}{Style.RESET_ALL}")
            return False
    
    def test_voltage_levels(self) -> bool:
        """Test voltage levels (requires multimeter).
        
        Returns:
            True if successful, False otherwise
        """
        print(f"{Fore.CYAN}Testing voltage levels...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}This test requires a multimeter{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please measure voltage between VCC and GND pins{Style.RESET_ALL}")
        
        voltage = input("Enter measured voltage (V): ")
        
        try:
            voltage_float = float(voltage)
            if 3.0 <= voltage_float <= 3.6:
                print(f"{Fore.GREEN}Voltage level correct: {voltage}V{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}Voltage level incorrect: {voltage}V (expected 3.3V){Style.RESET_ALL}")
                return False
        except ValueError:
            print(f"{Fore.RED}Invalid voltage value: {voltage}{Style.RESET_ALL}")
            return False
    
    def run_comprehensive_test(self) -> bool:
        """Run comprehensive connection test.
        
        Returns:
            True if all tests pass, False otherwise
        """
        print(f"{Fore.CYAN}Running comprehensive connection test...{Style.RESET_ALL}")
        print("=" * 60)
        
        tests = [
            ("Basic Connection", self.test_basic_connection),
            ("Loopback Test", self.test_loopback),
            ("Camera Boot", self.test_camera_boot),
            ("U-Boot Prompt", self.test_uboot_prompt),
            ("Command Execution", self.test_command_execution),
            ("Voltage Levels", self.test_voltage_levels)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{Fore.CYAN}Running: {test_name}{Style.RESET_ALL}")
            print("-" * 40)
            
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"{Fore.GREEN}✓ {test_name} PASSED{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}✗ {test_name} FAILED{Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"{Fore.RED}✗ {test_name} ERROR: {e}{Style.RESET_ALL}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print(f"{Fore.CYAN}Test Summary:{Style.RESET_ALL}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = f"{Fore.GREEN}PASSED{Style.RESET_ALL}" if result else f"{Fore.RED}FAILED{Style.RESET_ALL}"
            print(f"  {test_name}: {status}")
        
        print(f"\n{Fore.CYAN}Overall: {passed}/{total} tests passed{Style.RESET_ALL}")
        
        if passed == total:
            print(f"{Fore.GREEN}All tests passed! Connection is working properly.{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}Some tests failed. Check connections and settings.{Style.RESET_ALL}")
            return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='FTDI Connection Test for DCS-8000LH Camera',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python connection_test.py --port COM3
  python connection_test.py --port /dev/ttyUSB0 --baud 115200
  python connection_test.py --port COM3 --timeout 2.0 --verbose
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        required=True,
        help='Serial port (e.g., COM3, /dev/ttyUSB0)'
    )
    
    parser.add_argument(
        '--baud', '-b',
        type=int,
        default=115200,
        help='Baud rate (default: 115200)'
    )
    
    parser.add_argument(
        '--timeout', '-t',
        type=float,
        default=1.0,
        help='Timeout in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '--test', '-T',
        choices=['basic', 'loopback', 'boot', 'uboot', 'command', 'voltage', 'all'],
        default='all',
        help='Specific test to run (default: all)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    # Create connection tester
    tester = ConnectionTester(
        port=args.port,
        baud=args.baud,
        timeout=args.timeout
    )
    
    try:
        # Connect to serial port
        if not tester.connect():
            print(f"{Fore.RED}Failed to connect to {args.port}{Style.RESET_ALL}")
            sys.exit(1)
        
        # Run specific test
        if args.test == 'basic':
            success = tester.test_basic_connection()
        elif args.test == 'loopback':
            success = tester.test_loopback()
        elif args.test == 'boot':
            success = tester.test_camera_boot()
        elif args.test == 'uboot':
            success = tester.test_uboot_prompt()
        elif args.test == 'command':
            success = tester.test_command_execution()
        elif args.test == 'voltage':
            success = tester.test_voltage_levels()
        else:  # all
            success = tester.run_comprehensive_test()
        
        if success:
            print(f"\n{Fore.GREEN}Test completed successfully!{Style.RESET_ALL}")
            sys.exit(0)
        else:
            print(f"\n{Fore.RED}Test failed!{Style.RESET_ALL}")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)
    finally:
        tester.disconnect()


if __name__ == '__main__':
    main()
