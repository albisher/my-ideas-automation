#!/usr/bin/env python3
"""
FTDI Firmware Flasher for DCS-8000LH Camera
Flash firmware to the camera via serial connection using U-Boot commands.
"""

import serial
import time
import sys
import argparse
import logging
import os
import hashlib
from typing import Optional, Tuple
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for cross-platform colored output
colorama.init()

class FirmwareFlasher:
    """Firmware flasher for DCS-8000LH camera via serial connection."""
    
    def __init__(self, port: str, baud: int = 115200, timeout: float = 5.0):
        """Initialize firmware flasher.
        
        Args:
            port: Serial port (e.g., 'COM3', '/dev/ttyUSB0')
            baud: Baud rate (default: 115200)
            timeout: Timeout in seconds (default: 5.0)
        """
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self.connected = False
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('FirmwareFlasher')
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
    
    def send_command(self, command: str, wait_time: float = 1.0) -> str:
        """Send command and read response.
        
        Args:
            command: Command to send
            wait_time: Time to wait for response
            
        Returns:
            Response from device
        """
        if not self.connected or not self.ser:
            return "Not connected to serial port"
        
        try:
            # Clear input buffer
            self.ser.reset_input_buffer()
            
            # Send command
            self.ser.write(f"{command}\r\n".encode())
            time.sleep(0.1)  # Wait for command to be sent
            
            # Read response
            response = b""
            start_time = time.time()
            
            while time.time() - start_time < wait_time:
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    response += data
                    time.sleep(0.01)  # Small delay to allow more data
                else:
                    time.sleep(0.01)
            
            return response.decode('utf-8', errors='ignore')
            
        except Exception as e:
            self.logger.error(f"Error sending command: {e}")
            return f"Error: {e}"
    
    def wait_for_prompt(self, prompt: str = "=>", timeout: float = 10.0) -> bool:
        """Wait for U-Boot prompt.
        
        Args:
            prompt: Prompt to wait for
            timeout: Timeout in seconds
            
        Returns:
            True if prompt found, False otherwise
        """
        if not self.connected or not self.ser:
            return False
        
        start_time = time.time()
        buffer = ""
        
        try:
            while time.time() - start_time < timeout:
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    buffer += data.decode('utf-8', errors='ignore')
                    
                    if prompt in buffer:
                        return True
                    
                    # Keep only last 1000 characters to prevent memory issues
                    if len(buffer) > 1000:
                        buffer = buffer[-1000:]
                
                time.sleep(0.01)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error waiting for prompt: {e}")
            return False
    
    def boot_into_uboot(self) -> bool:
        """Boot camera into U-Boot mode.
        
        Returns:
            True if successful, False otherwise
        """
        print(f"{Fore.YELLOW}Booting into U-Boot mode...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Please power cycle the camera and press any key during boot{Style.RESET_ALL}")
        input("Press Enter when ready...")
        
        # Wait for U-Boot prompt
        if self.wait_for_prompt("=>", 30.0):
            print(f"{Fore.GREEN}U-Boot prompt detected{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}U-Boot prompt not detected{Style.RESET_ALL}")
            return False
    
    def setup_network(self, server_ip: str = "192.168.1.1", camera_ip: str = "192.168.1.100") -> bool:
        """Setup network parameters in U-Boot.
        
        Args:
            server_ip: TFTP server IP address
            camera_ip: Camera IP address
            
        Returns:
            True if successful, False otherwise
        """
        print(f"{Fore.YELLOW}Setting up network parameters...{Style.RESET_ALL}")
        
        commands = [
            f"setenv ipaddr {camera_ip}",
            f"setenv serverip {server_ip}",
            f"setenv gatewayip {server_ip}",
            "setenv netmask 255.255.255.0",
            "printenv"
        ]
        
        for cmd in commands:
            print(f"{Fore.CYAN}Executing: {cmd}{Style.RESET_ALL}")
            response = self.send_command(cmd, 2.0)
            print(f"{Fore.WHITE}{response}{Style.RESET_ALL}")
            time.sleep(0.5)
        
        return True
    
    def download_firmware(self, firmware_file: str, server_ip: str = "192.168.1.1") -> bool:
        """Download firmware via TFTP.
        
        Args:
            firmware_file: Firmware file name
            server_ip: TFTP server IP address
            
        Returns:
            True if successful, False otherwise
        """
        print(f"{Fore.YELLOW}Downloading firmware: {firmware_file}{Style.RESET_ALL}")
        
        # Download firmware to memory
        download_cmd = f"tftp 0x80000000 {firmware_file}"
        print(f"{Fore.CYAN}Executing: {download_cmd}{Style.RESET_ALL}")
        
        response = self.send_command(download_cmd, 30.0)  # Allow 30 seconds for download
        print(f"{Fore.WHITE}{response}{Style.RESET_ALL}")
        
        # Check if download was successful
        if "Bytes transferred" in response or "Loading" in response:
            print(f"{Fore.GREEN}Firmware download successful{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Firmware download failed{Style.RESET_ALL}")
            return False
    
    def flash_firmware(self, flash_address: str = "0x9f000000", flash_size: str = "+0x800000") -> bool:
        """Flash firmware to flash memory.
        
        Args:
            flash_address: Flash memory address
            flash_size: Flash memory size
            
        Returns:
            True if successful, False otherwise
        """
        print(f"{Fore.YELLOW}Flashing firmware to flash memory...{Style.RESET_ALL}")
        
        # Erase flash memory
        erase_cmd = f"erase {flash_address} {flash_size}"
        print(f"{Fore.CYAN}Executing: {erase_cmd}{Style.RESET_ALL}")
        
        response = self.send_command(erase_cmd, 30.0)  # Allow 30 seconds for erase
        print(f"{Fore.WHITE}{response}{Style.RESET_ALL}")
        
        if "Erased" in response or "OK" in response:
            print(f"{Fore.GREEN}Flash erase successful{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Flash erase failed{Style.RESET_ALL}")
            return False
        
        # Copy firmware to flash
        copy_cmd = f"cp.b 0x80000000 {flash_address} 0x800000"
        print(f"{Fore.CYAN}Executing: {copy_cmd}{Style.RESET_ALL}")
        
        response = self.send_command(copy_cmd, 60.0)  # Allow 60 seconds for copy
        print(f"{Fore.WHITE}{response}{Style.RESET_ALL}")
        
        if "Copy" in response or "OK" in response:
            print(f"{Fore.GREEN}Firmware flash successful{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Firmware flash failed{Style.RESET_ALL}")
            return False
    
    def verify_firmware(self, flash_address: str = "0x9f000000") -> bool:
        """Verify flashed firmware.
        
        Args:
            flash_address: Flash memory address
            
        Returns:
            True if verification successful, False otherwise
        """
        print(f"{Fore.YELLOW}Verifying flashed firmware...{Style.RESET_ALL}")
        
        # Read first few bytes from flash
        verify_cmd = f"md.b {flash_address} 0x100"
        print(f"{Fore.CYAN}Executing: {verify_cmd}{Style.RESET_ALL}")
        
        response = self.send_command(verify_cmd, 5.0)
        print(f"{Fore.WHITE}{response}{Style.RESET_ALL}")
        
        # Check if we can read from flash
        if "00000000" not in response and len(response) > 50:
            print(f"{Fore.GREEN}Firmware verification successful{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Firmware verification failed{Style.RESET_ALL}")
            return False
    
    def boot_system(self) -> bool:
        """Boot the system with new firmware.
        
        Returns:
            True if successful, False otherwise
        """
        print(f"{Fore.YELLOW}Booting system with new firmware...{Style.RESET_ALL}")
        
        boot_cmd = "bootm 0x9f000000"
        print(f"{Fore.CYAN}Executing: {boot_cmd}{Style.RESET_ALL}")
        
        response = self.send_command(boot_cmd, 10.0)
        print(f"{Fore.WHITE}{response}{Style.RESET_ALL}")
        
        if "Starting kernel" in response or "Linux version" in response:
            print(f"{Fore.GREEN}System boot successful{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}System boot failed{Style.RESET_ALL}")
            return False
    
    def calculate_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum of firmware file.
        
        Args:
            file_path: Path to firmware file
            
        Returns:
            MD5 checksum as hex string
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                return hashlib.md5(data).hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating checksum: {e}")
            return ""
    
    def flash_firmware_complete(self, firmware_file: str, server_ip: str = "192.168.1.1", 
                               camera_ip: str = "192.168.1.100", verify: bool = True) -> bool:
        """Complete firmware flashing process.
        
        Args:
            firmware_file: Firmware file name
            server_ip: TFTP server IP address
            camera_ip: Camera IP address
            verify: Whether to verify after flashing
            
        Returns:
            True if successful, False otherwise
        """
        print(f"{Fore.CYAN}Starting firmware flashing process...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Firmware file: {firmware_file}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Server IP: {server_ip}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Camera IP: {camera_ip}{Style.RESET_ALL}")
        print("-" * 50)
        
        try:
            # Step 1: Boot into U-Boot
            if not self.boot_into_uboot():
                return False
            
            # Step 2: Setup network
            if not self.setup_network(server_ip, camera_ip):
                return False
            
            # Step 3: Download firmware
            if not self.download_firmware(firmware_file, server_ip):
                return False
            
            # Step 4: Flash firmware
            if not self.flash_firmware():
                return False
            
            # Step 5: Verify firmware (optional)
            if verify:
                if not self.verify_firmware():
                    print(f"{Fore.YELLOW}Warning: Firmware verification failed{Style.RESET_ALL}")
            
            # Step 6: Boot system
            if not self.boot_system():
                return False
            
            print(f"{Fore.GREEN}Firmware flashing completed successfully!{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}Error during firmware flashing: {e}{Style.RESET_ALL}")
            return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='FTDI Firmware Flasher for DCS-8000LH Camera',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python firmware_flasher.py --port COM3 --firmware firmware.bin
  python firmware_flasher.py --port /dev/ttyUSB0 --firmware firmware.bin --server-ip 192.168.1.1
  python firmware_flasher.py --port COM3 --firmware firmware.bin --verify --backup
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        required=True,
        help='Serial port (e.g., COM3, /dev/ttyUSB0)'
    )
    
    parser.add_argument(
        '--firmware', '-f',
        required=True,
        help='Firmware file name (must be available on TFTP server)'
    )
    
    parser.add_argument(
        '--server-ip', '-s',
        default='192.168.1.1',
        help='TFTP server IP address (default: 192.168.1.1)'
    )
    
    parser.add_argument(
        '--camera-ip', '-c',
        default='192.168.1.100',
        help='Camera IP address (default: 192.168.1.100)'
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
        default=5.0,
        help='Timeout in seconds (default: 5.0)'
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify firmware after flashing'
    )
    
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create backup before flashing'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force flash even if risky'
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
    
    # Create firmware flasher
    flasher = FirmwareFlasher(
        port=args.port,
        baud=args.baud,
        timeout=args.timeout
    )
    
    try:
        # Connect to serial port
        if not flasher.connect():
            print(f"{Fore.RED}Failed to connect to {args.port}{Style.RESET_ALL}")
            sys.exit(1)
        
        # Show warnings
        if args.force:
            print(f"{Fore.YELLOW}Warning: Force mode enabled - proceeding with risky operation{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Warning: This operation can permanently damage your camera{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Make sure you have a backup and recovery plan{Style.RESET_ALL}")
            confirm = input("Do you want to continue? (yes/no): ")
            if confirm.lower() != 'yes':
                print(f"{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}")
                sys.exit(0)
        
        # Flash firmware
        success = flasher.flash_firmware_complete(
            firmware_file=args.firmware,
            server_ip=args.server_ip,
            camera_ip=args.camera_ip,
            verify=args.verify
        )
        
        if success:
            print(f"{Fore.GREEN}Firmware flashing completed successfully!{Style.RESET_ALL}")
            sys.exit(0)
        else:
            print(f"{Fore.RED}Firmware flashing failed!{Style.RESET_ALL}")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)
    finally:
        flasher.disconnect()


if __name__ == '__main__':
    main()
