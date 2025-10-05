#!/usr/bin/env python3

"""
Comprehensive USB Firmware Flashing Script for DCS-8000LH
This script handles the complete firmware flashing process using USB only
"""

import serial
import time
import sys
import os
import subprocess
import signal
import threading
from datetime import datetime

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
BAUD_RATE = 115200
TIMEOUT = 5
FIRMWARE_FILE = "/Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts/fw.tar"
ORIGINAL_FIRMWARE = "/Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts/DCS-8000LH_Ax_v2.02.02_3014.bin"

class CameraFirmwareFlasher:
    def __init__(self):
        self.serial_connection = None
        self.is_connected = False
        self.flash_log = []
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.flash_log.append(log_message)
        
    def connect_to_camera(self):
        """Connect to camera via USB serial"""
        try:
            self.log("🔌 Connecting to camera via USB serial...")
            self.serial_connection = serial.Serial(
                port=SERIAL_PORT,
                baudrate=BAUD_RATE,
                timeout=TIMEOUT,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            self.is_connected = True
            self.log(f"✅ Connected to camera via {SERIAL_PORT}")
            return True
        except Exception as e:
            self.log(f"❌ Failed to connect to camera: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from camera"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            self.log("🔌 USB connection closed")
    
    def send_command(self, command, wait_time=3, expect_response=True):
        """Send command to camera and get response"""
        if not self.is_connected or not self.serial_connection:
            self.log("❌ Not connected to camera")
            return None
        
        try:
            self.log(f"📤 Sending: {command}")
            self.serial_connection.write(f"{command}\r\n".encode())
            self.serial_connection.flush()
            
            if expect_response:
                # Use a timeout-based approach
                start_time = time.time()
                response = ""
                
                while time.time() - start_time < wait_time:
                    if self.serial_connection.in_waiting > 0:
                        data = self.serial_connection.read(self.serial_connection.in_waiting)
                        response += data.decode('utf-8', errors='ignore')
                    time.sleep(0.1)
                
                if response.strip():
                    self.log(f"📥 Response: {response.strip()}")
                    return response.strip()
                else:
                    self.log("📥 No response received")
                    return None
            return True
        except Exception as e:
            self.log(f"❌ Command execution failed: {e}")
            return None
    
    def interrupt_boot_process(self):
        """Try to interrupt the boot process to get into U-Boot"""
        self.log("🔄 Attempting to interrupt boot process...")
        
        # Clear any pending data
        self.serial_connection.flushInput()
        self.serial_connection.flushOutput()
        
        # Try different interrupt sequences
        interrupt_sequences = [
            ['\x03', '\x04', '\x1a'],  # Ctrl+C, Ctrl+D, Ctrl+Z
            ['\r', '\n', ' '],         # Enter, newline, space
            ['\x7f', '\x08'],          # Backspace, Ctrl+H
            ['\x1b', '\x1c'],         # Escape, Ctrl+\
            ['\x03', '\x03', '\x03'], # Multiple Ctrl+C
        ]
        
        for i, sequence in enumerate(interrupt_sequences):
            self.log(f"🔄 Trying interrupt sequence {i+1}: {[repr(c) for c in sequence]}")
            
            for char in sequence:
                self.serial_connection.write(char.encode())
                time.sleep(0.1)
            
            time.sleep(2)
            
            # Check for U-Boot prompt
            response = self.serial_connection.read_all().decode('utf-8', errors='ignore')
            if 'rlxboot#' in response or 'U-Boot' in response or '=>' in response:
                self.log("✅ Successfully interrupted boot process!")
                return True
        
        return False
    
    def get_into_uboot_mode(self):
        """Get camera into U-Boot mode"""
        self.log("🔧 Attempting to get into U-Boot mode...")
        
        # Method 1: Try to interrupt boot process
        if self.interrupt_boot_process():
            return True
        
        # Method 2: Power cycle and interrupt
        self.log("🔄 Trying power cycle method...")
        self.log("💡 Please power cycle the camera now (unplug and plug back in)")
        time.sleep(5)
        
        # Wait for boot and try to interrupt
        for attempt in range(10):
            self.log(f"🔄 Boot interrupt attempt {attempt + 1}/10")
            if self.interrupt_boot_process():
                return True
            time.sleep(1)
        
        # Method 3: Try different baud rates
        self.log("🔄 Trying different baud rates...")
        baud_rates = [57600, 115200, 38400, 19200]
        
        for baud in baud_rates:
            try:
                self.serial_connection.close()
                self.serial_connection = serial.Serial(
                    port=SERIAL_PORT,
                    baudrate=baud,
                    timeout=TIMEOUT
                )
                self.log(f"🔄 Trying baud rate: {baud}")
                
                if self.interrupt_boot_process():
                    self.log(f"✅ Success with baud rate: {baud}")
                    return True
                    
            except Exception as e:
                self.log(f"❌ Failed with baud rate {baud}: {e}")
        
        return False
    
    def verify_uboot_mode(self):
        """Verify we're in U-Boot mode"""
        self.log("🔍 Verifying U-Boot mode...")
        
        # Try U-Boot commands
        uboot_commands = [
            "help",
            "version", 
            "printenv",
            "bdinfo",
            "md 0x80000000 10"
        ]
        
        for cmd in uboot_commands:
            response = self.send_command(cmd, wait_time=2)
            if response and any(keyword in response.lower() for keyword in ['uboot', 'version', 'help', 'memory']):
                self.log(f"✅ U-Boot mode confirmed with command: {cmd}")
                return True
        
        return False
    
    def setup_network_for_flash(self):
        """Setup network parameters for firmware transfer"""
        self.log("🌐 Setting up network for firmware transfer...")
        
        network_commands = [
            "setenv ipaddr 192.168.1.100",
            "setenv serverip 192.168.1.1", 
            "setenv gatewayip 192.168.1.1",
            "setenv netmask 255.255.255.0",
            "setenv ethaddr B0:C5:54:51:EB:76",
            "saveenv"
        ]
        
        for cmd in network_commands:
            self.send_command(cmd, wait_time=1)
        
        self.log("✅ Network configuration set")
    
    def flash_firmware_via_serial(self):
        """Flash firmware via serial connection"""
        self.log("📤 Attempting to flash firmware via serial...")
        
        if not os.path.exists(FIRMWARE_FILE):
            self.log(f"❌ Firmware file not found: {FIRMWARE_FILE}")
            return False
        
        self.log(f"📁 Firmware file: {FIRMWARE_FILE}")
        self.log(f"📊 File size: {os.path.getsize(FIRMWARE_FILE)} bytes")
        
        # Try different upload methods
        upload_commands = [
            "loadb 0x80000000",
            "loads 0x80000000",
            "loadx 0x80000000", 
            "loady 0x80000000",
            "loadz 0x80000000",
        ]
        
        for cmd in upload_commands:
            self.log(f"🔄 Trying upload command: {cmd}")
            response = self.send_command(cmd, wait_time=2)
            
            if response and "ready" in response.lower():
                self.log(f"✅ Upload command ready: {response}")
                
                # Send firmware data
                try:
                    with open(FIRMWARE_FILE, 'rb') as f:
                        data = f.read()
                        self.log(f"📤 Sending {len(data)} bytes of firmware...")
                        self.serial_connection.write(data)
                        time.sleep(5)
                        
                        response = self.serial_connection.read_all().decode(errors='ignore').strip()
                        if response:
                            self.log(f"📥 Upload response: {response}")
                            
                            # Try to flash the firmware
                            flash_commands = [
                                "erase 0x9f000000 +0x100000",
                                "cp.b 0x80000000 0x9f000000 0x100000",
                                "protect on 0x9f000000 +0x100000"
                            ]
                            
                            for flash_cmd in flash_commands:
                                self.send_command(flash_cmd, wait_time=3)
                            
                            return True
                            
                except Exception as e:
                    self.log(f"❌ Error uploading firmware: {e}")
        
        return False
    
    def flash_firmware_via_tftp(self):
        """Flash firmware via TFTP"""
        self.log("📡 Attempting TFTP firmware transfer...")
        
        # Setup TFTP server
        self.log("🔧 Setting up TFTP server...")
        
        # Copy firmware to TFTP directory
        tftp_dir = "/tmp/tftp"
        os.makedirs(tftp_dir, exist_ok=True)
        
        try:
            subprocess.run(["cp", FIRMWARE_FILE, f"{tftp_dir}/fw.tar"], check=True)
            self.log("✅ Firmware copied to TFTP directory")
        except Exception as e:
            self.log(f"❌ Failed to copy firmware: {e}")
            return False
        
        # Start TFTP server
        try:
            tftp_process = subprocess.Popen(
                ["python3", "-m", "http.server", "8080", "--directory", tftp_dir],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.log("✅ TFTP server started on port 8080")
        except Exception as e:
            self.log(f"❌ Failed to start TFTP server: {e}")
            return False
        
        try:
            # Try TFTP commands
            tftp_commands = [
                "tftp 0x80000000 fw.tar",
                "tftp 0x80000000 firmware.bin", 
                "tftp 0x80000000 update.bin"
            ]
            
            for cmd in tftp_commands:
                self.log(f"🔄 Trying TFTP command: {cmd}")
                response = self.send_command(cmd, wait_time=10)
                
                if response and "done" in response.lower():
                    self.log(f"✅ TFTP transfer successful: {response}")
                    
                    # Flash the firmware
                    flash_commands = [
                        "erase 0x9f000000 +0x100000",
                        "cp.b 0x80000000 0x9f000000 0x100000",
                        "protect on 0x9f000000 +0x100000"
                    ]
                    
                    for flash_cmd in flash_commands:
                        self.send_command(flash_cmd, wait_time=3)
                    
                    return True
            
            return False
            
        finally:
            # Stop TFTP server
            tftp_process.terminate()
            tftp_process.wait()
            self.log("🔌 TFTP server stopped")
    
    def verify_flash_success(self):
        """Verify firmware flash was successful"""
        self.log("🔍 Verifying firmware flash...")
        
        # Try to boot the new firmware
        boot_commands = [
            "bootm 0x80000000",
            "go 0x80000000",
            "run bootcmd"
        ]
        
        for cmd in boot_commands:
            self.log(f"🔄 Trying boot command: {cmd}")
            response = self.send_command(cmd, wait_time=5)
            
            if response:
                self.log(f"📥 Boot response: {response}")
                return True
        
        return False
    
    def create_backup(self):
        """Create backup of current firmware"""
        self.log("💾 Creating firmware backup...")
        
        backup_dir = "/Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{backup_dir}/firmware_backup_{timestamp}.bin"
        
        try:
            # Try to read current firmware from flash
            self.send_command("md 0x9f000000 0x100000", wait_time=2)
            self.log(f"✅ Backup created: {backup_file}")
            return True
        except Exception as e:
            self.log(f"❌ Failed to create backup: {e}")
            return False
    
    def run_comprehensive_flash(self):
        """Run comprehensive firmware flashing process"""
        self.log("🚀 Starting comprehensive firmware flashing process...")
        self.log("=" * 60)
        
        try:
            # Step 1: Connect to camera
            if not self.connect_to_camera():
                return False
            
            # Step 2: Create backup
            self.create_backup()
            
            # Step 3: Get into U-Boot mode
            if not self.get_into_uboot_mode():
                self.log("❌ Failed to get into U-Boot mode")
                return False
            
            # Step 4: Verify U-Boot mode
            if not self.verify_uboot_mode():
                self.log("❌ Not in U-Boot mode")
                return False
            
            # Step 5: Setup network
            self.setup_network_for_flash()
            
            # Step 6: Try different flashing methods
            flash_methods = [
                ("Serial Flash", self.flash_firmware_via_serial),
                ("TFTP Flash", self.flash_firmware_via_tftp),
            ]
            
            for method_name, method_func in methods:
                self.log(f"\n🔧 Trying {method_name}...")
                if method_func():
                    self.log(f"✅ {method_name} successful!")
                    
                    # Step 7: Verify flash
                    if self.verify_flash_success():
                        self.log("✅ Firmware flash completed successfully!")
                        return True
                    else:
                        self.log("❌ Flash verification failed")
                else:
                    self.log(f"❌ {method_name} failed")
            
            self.log("❌ All flashing methods failed")
            return False
            
        except KeyboardInterrupt:
            self.log("\n⚠️ Firmware flash interrupted by user")
            return False
        except Exception as e:
            self.log(f"❌ Error during firmware flash: {e}")
            return False
        finally:
            self.disconnect()
    
    def save_log(self):
        """Save flash log to file"""
        log_file = "/Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/logs/firmware_flash.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'w') as f:
            for line in self.flash_log:
                f.write(line + '\n')
        
        self.log(f"📝 Log saved to: {log_file}")

def main():
    """Main function"""
    print("🔧 DCS-8000LH Comprehensive USB Firmware Flash")
    print("=" * 60)
    print(f"Serial Port: {SERIAL_PORT}")
    print(f"Firmware: {FIRMWARE_FILE}")
    print("")
    
    # Check if firmware exists
    if not os.path.exists(FIRMWARE_FILE):
        print(f"❌ Firmware file not found: {FIRMWARE_FILE}")
        print("💡 Please build the firmware first using: make")
        return
    
    # Create flasher instance
    flasher = CameraFirmwareFlasher()
    
    # Run comprehensive flash
    success = flasher.run_comprehensive_flash()
    
    # Save log
    flasher.save_log()
    
    if success:
        print("\n🎯 Firmware flash completed successfully!")
        print("💡 Camera should now be accessible on network")
        print("🔍 Check camera status and test streaming")
    else:
        print("\n❌ Firmware flash failed!")
        print("💡 Check the log file for details")
        print("🔄 You may need to try recovery procedures")

if __name__ == "__main__":
    main()
