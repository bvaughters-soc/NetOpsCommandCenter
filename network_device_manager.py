#!/usr/bin/env python3
"""
Network Device Manager for ISP Equipment
Supports SSH/Telnet connections to various network devices
"""

import paramiko
import telnetlib
import time
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """Supported device types"""
    CIENA = "ciena"
    BROCADE_CES = "brocade_ces"
    BROCADE_ICX = "brocade_icx"
    BROCADE_FWS = "brocade_fws"
    ALCATEL_7210 = "alcatel_7210"


class ConnectionType(Enum):
    """Connection protocol types"""
    SSH = "ssh"
    TELNET = "telnet"


@dataclass
class DeviceCredentials:
    """Device connection credentials"""
    ip_address: str
    username: str
    password: str
    enable_password: Optional[str] = None
    port: Optional[int] = None
    device_type: DeviceType = DeviceType.MIKROTIK
    connection_type: ConnectionType = ConnectionType.SSH
    timeout: int = 30


class DeviceCommands:
    """Command sets for different device types"""
    
    BASIC_COMMANDS = {
        DeviceType.CIENA: [
            "software show",
            "system show",
            "port show",
            "configuration show",
        ],
        DeviceType.BROCADE_CES: [
            "show version",
            "show system",
            "show running-config",
            "show interface brief",
        ],
        DeviceType.BROCADE_ICX: [
            "show version",
            "show running-config",
            "show interface brief",
            "show ip interface brief",
        ],
        DeviceType.BROCADE_FWS: [
            "show version",
            "show system",
            "show interface status",
        ],
        DeviceType.ALCATEL_7210: [
            "show version",
            "show system information",
            "show router interface",
            "show card state",
        ],
    }
    
    @classmethod
    def get_basic_commands(cls, device_type: DeviceType) -> List[str]:
        """Get basic diagnostic commands for a device type"""
        return cls.BASIC_COMMANDS.get(device_type, [])


class NetworkDevice:
    """Base class for network device connections"""
    
    def __init__(self, credentials: DeviceCredentials):
        self.credentials = credentials
        self.connection = None
        self.output_buffer = []
        
    def connect(self):
        """Connect to the device - to be implemented by subclasses"""
        raise NotImplementedError
        
    def disconnect(self):
        """Disconnect from the device - to be implemented by subclasses"""
        raise NotImplementedError
        
    def send_command(self, command: str, delay: float = 1.0) -> str:
        """Send command to device - to be implemented by subclasses"""
        raise NotImplementedError
        
    def send_commands(self, commands: List[str], delay: float = 1.0) -> Dict[str, str]:
        """Send multiple commands and return results"""
        results = {}
        for command in commands:
            logger.info(f"Executing command: {command}")
            output = self.send_command(command, delay)
            results[command] = output
        return results


class SSHDevice(NetworkDevice):
    """SSH connection handler for network devices"""
    
    def connect(self):
        """Establish SSH connection to device"""
        try:
            self.connection = paramiko.SSHClient()
            self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            port = self.credentials.port or 22
            
            logger.info(f"Connecting via SSH to {self.credentials.ip_address}:{port}")
            self.connection.connect(
                hostname=self.credentials.ip_address,
                port=port,
                username=self.credentials.username,
                password=self.credentials.password,
                timeout=self.credentials.timeout,
                look_for_keys=False,
                allow_agent=False
            )
            
            # Start interactive shell
            self.shell = self.connection.invoke_shell()
            time.sleep(1)
            
            # Clear initial buffer
            if self.shell.recv_ready():
                initial_output = self.shell.recv(65535).decode('utf-8', errors='ignore')
                logger.debug(f"Initial output: {initial_output}")
            
            # Enter enable mode if enable password is provided
            if self.credentials.enable_password:
                logger.info("Entering privileged mode...")
                self._enter_enable_mode()
            
            logger.info("SSH connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"SSH connection failed: {str(e)}")
            raise
    
    def _enter_enable_mode(self):
        """Enter privileged/enable mode on the device"""
        try:
            # Send enable command
            self.shell.send('enable\n')
            time.sleep(0.5)
            
            # Wait for password prompt
            output = ""
            while self.shell.recv_ready():
                output += self.shell.recv(65535).decode('utf-8', errors='ignore')
                time.sleep(0.1)
            
            # Send enable password
            self.shell.send(self.credentials.enable_password + '\n')
            time.sleep(0.5)
            
            # Clear buffer
            while self.shell.recv_ready():
                self.shell.recv(65535)
                time.sleep(0.1)
            
            logger.info("Successfully entered privileged mode")
            
        except Exception as e:
            logger.warning(f"Failed to enter enable mode: {str(e)}")
            # Don't raise - some devices may not need enable mode
    
    def disconnect(self):
        """Close SSH connection"""
        if self.connection:
            self.connection.close()
            logger.info("SSH connection closed")
    
    def send_command(self, command: str, delay: float = 1.0) -> str:
        """Send command via SSH and return output"""
        if not self.shell:
            raise Exception("No active connection")
        
        # Send command
        self.shell.send(command + '\n')
        time.sleep(delay)
        
        # Receive output
        output = ""
        while self.shell.recv_ready():
            output += self.shell.recv(65535).decode('utf-8', errors='ignore')
            time.sleep(0.1)
        
        return output


class TelnetDevice(NetworkDevice):
    """Telnet connection handler for network devices"""
    
    def connect(self):
        """Establish Telnet connection to device"""
        try:
            port = self.credentials.port or 23
            
            logger.info(f"Connecting via Telnet to {self.credentials.ip_address}:{port}")
            self.connection = telnetlib.Telnet(
                self.credentials.ip_address,
                port,
                timeout=self.credentials.timeout
            )
            
            # Wait for username prompt
            self.connection.read_until(b"login: ", timeout=5)
            self.connection.write(self.credentials.username.encode('ascii') + b'\n')
            
            # Wait for password prompt
            self.connection.read_until(b"Password: ", timeout=5)
            self.connection.write(self.credentials.password.encode('ascii') + b'\n')
            
            time.sleep(2)
            
            # Clear initial buffer
            self.connection.read_very_eager()
            
            # Enter enable mode if enable password is provided
            if self.credentials.enable_password:
                logger.info("Entering privileged mode...")
                self._enter_enable_mode()
            
            logger.info("Telnet connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Telnet connection failed: {str(e)}")
            raise
    
    def _enter_enable_mode(self):
        """Enter privileged/enable mode on the device"""
        try:
            # Send enable command
            self.connection.write(b'enable\n')
            time.sleep(0.5)
            
            # Wait for password prompt
            self.connection.read_until(b"Password: ", timeout=3)
            
            # Send enable password
            self.connection.write(self.credentials.enable_password.encode('ascii') + b'\n')
            time.sleep(0.5)
            
            # Clear buffer
            self.connection.read_very_eager()
            
            logger.info("Successfully entered privileged mode")
            
        except Exception as e:
            logger.warning(f"Failed to enter enable mode: {str(e)}")
            # Don't raise - some devices may not need enable mode
    
    def disconnect(self):
        """Close Telnet connection"""
        if self.connection:
            self.connection.close()
            logger.info("Telnet connection closed")
    
    def send_command(self, command: str, delay: float = 1.0) -> str:
        """Send command via Telnet and return output"""
        if not self.connection:
            raise Exception("No active connection")
        
        self.connection.write(command.encode('ascii') + b'\n')
        time.sleep(delay)
        
        output = self.connection.read_very_eager().decode('utf-8', errors='ignore')
        return output


class DeviceManager:
    """Main manager class for device operations"""
    
    def __init__(self):
        self.devices = {}
    
    def create_device(self, credentials: DeviceCredentials) -> NetworkDevice:
        """Create appropriate device connection based on credentials"""
        if credentials.connection_type == ConnectionType.SSH:
            return SSHDevice(credentials)
        elif credentials.connection_type == ConnectionType.TELNET:
            return TelnetDevice(credentials)
        else:
            raise ValueError(f"Unsupported connection type: {credentials.connection_type}")
    
    def execute_commands(
        self,
        credentials: DeviceCredentials,
        commands: Optional[List[str]] = None,
        use_basic_commands: bool = False
    ) -> Dict[str, str]:
        """
        Connect to device and execute commands
        
        Args:
            credentials: Device connection credentials
            commands: List of commands to execute (optional)
            use_basic_commands: Use predefined basic commands for device type
            
        Returns:
            Dictionary mapping commands to their outputs
        """
        device = self.create_device(credentials)
        
        try:
            # Connect to device
            device.connect()
            
            # Determine which commands to run
            if use_basic_commands:
                commands = DeviceCommands.get_basic_commands(credentials.device_type)
            
            if not commands:
                raise ValueError("No commands specified")
            
            # Execute commands
            results = device.send_commands(commands)
            
            return results
            
        finally:
            # Always disconnect
            device.disconnect()
    
    def save_results(self, results: Dict[str, str], filename: str):
        """Save command results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {filename}")


# Example usage
if __name__ == "__main__":
    # Example configuration
    credentials = DeviceCredentials(
        ip_address="192.168.1.1",
        username="admin",
        password="password",
        device_type=DeviceType.CIENA,
        connection_type=ConnectionType.SSH
    )
    
    manager = DeviceManager()
    
    try:
        # Run basic commands
        print("Executing basic commands...")
        results = manager.execute_commands(credentials, use_basic_commands=True)
        
        # Display results
        for command, output in results.items():
            print(f"\n{'='*60}")
            print(f"Command: {command}")
            print(f"{'='*60}")
            print(output)
        
        # Save to file
        manager.save_results(results, "device_output.json")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
