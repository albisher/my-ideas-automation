#!/usr/bin/env python3
"""
FTDI Serial Console for DCS-8000LH Camera
Interactive serial console for direct communication with the camera.
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

class SerialConsole:
    """Interactive serial console for DCS-8000LH camera communication."""
    
    def __init__(self, port: str, baud: int = 115200, timeout: float = 1.0):
        """Initialize serial console.
        
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
        logger = logging.getLogger('SerialConsole')
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
    
    def send_command(self, command: str) -> str:
        """Send command and read response.
        
        Args:
            command: Command to send
            
        Returns:
            Response from device
        """
        if not self.connected or not self.ser:
            return "Not connected to serial port"
        
        try:
            # Send command
            self.ser.write(f"{command}\r\n".encode())
            time.sleep(0.1)  # Wait for command to be sent
            
            # Read response
            response = b""
            start_time = time.time()
            
            while time.time() - start_time < self.timeout:
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
    
    def read_continuous(self, duration: float = 10.0) -> List[str]:
        """Read continuous output for specified duration.
        
        Args:
            duration: Duration in seconds
            
        Returns:
            List of received lines
        """
        if not self.connected or not self.ser:
            return ["Not connected to serial port"]
        
        lines = []
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    lines.append(data.decode('utf-8', errors='ignore'))
                time.sleep(0.01)
                
        except Exception as e:
            self.logger.error(f"Error reading continuous output: {e}")
            lines.append(f"Error: {e}")
        
        return lines
    
    def interactive_mode(self) -> None:
        """Start interactive console mode."""
        if not self.connected:
            print(f"{Fore.RED}Not connected to serial port{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}Serial Console - Interactive Mode{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Connected to {self.port} at {self.baud} baud{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Type 'help' for available commands, 'quit' to exit{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Type 'monitor' to start continuous monitoring{Style.RESET_ALL}")
        print("-" * 50)
        
        command_history = []
        
        while True:
            try:
                # Get user input
                command = input(f"{Fore.GREEN}DCS-8000LH> {Style.RESET_ALL}").strip()
                
                if not command:
                    continue
                
                # Handle special commands
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command.lower() == 'help':
                    self._show_help()
                    continue
                elif command.lower() == 'monitor':
                    self._monitor_mode()
                    continue
                elif command.lower() == 'history':
                    self._show_history(command_history)
                    continue
                elif command.lower() == 'clear':
                    self._clear_screen()
                    continue
                
                # Add to history
                command_history.append(command)
                
                # Send command and display response
                print(f"{Fore.BLUE}Sending: {command}{Style.RESET_ALL}")
                response = self.send_command(command)
                
                if response:
                    print(f"{Fore.WHITE}{response}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}No response received{Style.RESET_ALL}")
                
                print()  # Empty line for readability
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
                break
            except EOFError:
                print(f"\n{Fore.YELLOW}End of input{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    
    def _show_help(self) -> None:
        """Show available commands."""
        help_text = f"""
{Fore.CYAN}Available Commands:{Style.RESET_ALL}

{Fore.GREEN}System Commands:{Style.RESET_ALL}
  help                    - Show this help message
  quit/exit/q             - Exit the console
  monitor                 - Start continuous monitoring
  history                 - Show command history
  clear                   - Clear screen
  
{Fore.GREEN}U-Boot Commands:{Style.RESET_ALL}
  help                    - Show U-Boot help
  printenv                - Print environment variables
  setenv <var> <value>    - Set environment variable
  saveenv                 - Save environment
  boot                    - Boot system
  reset                   - Reset system
  
{Fore.GREEN}Linux Commands:{Style.RESET_ALL}
  cat /proc/version       - Show kernel version
  cat /proc/cpuinfo       - Show CPU information
  cat /proc/meminfo        - Show memory information
  ifconfig                - Show network interfaces
  route -n                - Show routing table
  ps aux                  - Show running processes
  netstat -tlnp           - Show listening ports
  logread                 - Show system logs
  dmesg                   - Show kernel messages
  
{Fore.GREEN}Camera Commands:{Style.RESET_ALL}
  /etc/init.d/camera status    - Check camera service
  /etc/init.d/streaming status - Check streaming service
  cat /etc/camera.conf         - Show camera configuration
  cat /etc/network.conf        - Show network configuration
"""
        print(help_text)
    
    def _monitor_mode(self) -> None:
        """Start monitoring mode."""
        print(f"{Fore.CYAN}Starting continuous monitoring...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop{Style.RESET_ALL}")
        print("-" * 50)
        
        try:
            while True:
                lines = self.read_continuous(1.0)  # Read for 1 second
                for line in lines:
                    if line.strip():
                        print(f"{Fore.WHITE}{line.strip()}{Style.RESET_ALL}")
                time.sleep(0.1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Monitoring stopped{Style.RESET_ALL}")
    
    def _show_history(self, history: List[str]) -> None:
        """Show command history."""
        if not history:
            print(f"{Fore.YELLOW}No commands in history{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}Command History:{Style.RESET_ALL}")
        for i, cmd in enumerate(history[-10:], 1):  # Show last 10 commands
            print(f"{i:2d}. {cmd}")
    
    def _clear_screen(self) -> None:
        """Clear screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='FTDI Serial Console for DCS-8000LH Camera',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python serial_console.py --port COM3
  python serial_console.py --port /dev/ttyUSB0 --baud 115200
  python serial_console.py --port COM3 --timeout 2.0 --log
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
        '--log',
        action='store_true',
        help='Enable logging to file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Create serial console
    console = SerialConsole(
        port=args.port,
        baud=args.baud,
        timeout=args.timeout
    )
    
    # Setup logging if requested
    if args.log:
        logging.basicConfig(
            level=logging.DEBUG if args.verbose else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('serial_console.log'),
                logging.StreamHandler()
            ]
        )
    
    try:
        # Connect to serial port
        if not console.connect():
            print(f"{Fore.RED}Failed to connect to {args.port}{Style.RESET_ALL}")
            sys.exit(1)
        
        # Start interactive mode
        console.interactive_mode()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)
    finally:
        console.disconnect()


if __name__ == '__main__':
    main()
