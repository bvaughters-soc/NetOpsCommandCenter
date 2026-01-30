#!/usr/bin/env python3
"""
NetOps Command Center - Python SDK
Easy-to-use Python wrapper for the NetOps API
"""

import requests
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
import json


@dataclass
class DeviceConfig:
    """Configuration for a network device"""
    ip_address: str
    username: str
    password: str
    device_type: str
    connection_type: str = "ssh"
    port: Optional[int] = None
    enable_password: Optional[str] = None
    timeout: int = 30
    name: Optional[str] = None


class NetOpsAPIError(Exception):
    """Custom exception for API errors"""
    pass


class NetOpsClient:
    """
    Python client for NetOps Command Center API
    
    Example:
        client = NetOpsClient("http://localhost:5000")
        
        # Single device
        result = client.execute(
            ip="192.168.1.1",
            username="admin",
            password="pass",
            device_type="brocade_icx"
        )
        
        # Batch execution
        devices = [
            DeviceConfig(ip_address="192.168.1.1", username="admin", 
                        password="pass", device_type="brocade_icx"),
            DeviceConfig(ip_address="192.168.1.2", username="admin",
                        password="pass", device_type="ciena")
        ]
        results = client.batch_execute(devices)
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost:5000",
        api_key: Optional[str] = None,
        timeout: int = 60
    ):
        """
        Initialize NetOps API client
        
        Args:
            base_url: Base URL of the API server
            api_key: Optional API key for authentication
            timeout: Default timeout for requests in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.timeout = timeout
        
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request to API"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise NetOpsAPIError(f"Request timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError:
            raise NetOpsAPIError(f"Cannot connect to {self.base_url}")
        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', str(e))
            except:
                error_msg = str(e)
            raise NetOpsAPIError(f"HTTP {response.status_code}: {error_msg}")
        except Exception as e:
            raise NetOpsAPIError(f"Request failed: {str(e)}")
    
    def health_check(self) -> Dict:
        """
        Check API health status
        
        Returns:
            Dict with status, timestamp, and cached_results count
        """
        return self._request('GET', '/health')
    
    def is_healthy(self) -> bool:
        """
        Check if API is healthy
        
        Returns:
            True if API is responding and healthy
        """
        try:
            response = self.health_check()
            return response.get('status') == 'healthy'
        except:
            return False
    
    def get_device_types(self) -> List[Dict]:
        """
        Get list of supported device types
        
        Returns:
            List of device type dictionaries with 'value' and 'label'
        """
        response = self._request('GET', '/device-types')
        if not response.get('success'):
            raise NetOpsAPIError(response.get('error', 'Failed to get device types'))
        return response.get('device_types', [])
    
    def get_basic_commands(self, device_type: str) -> List[str]:
        """
        Get basic commands for a device type
        
        Args:
            device_type: Type of device (e.g., 'brocade_icx', 'ciena')
            
        Returns:
            List of command strings
        """
        data = {'device_type': device_type}
        response = self._request('POST', '/basic-commands', data=data)
        if not response.get('success'):
            raise NetOpsAPIError(response.get('error', 'Failed to get commands'))
        return response.get('commands', [])
    
    def execute(
        self,
        ip: str,
        username: str,
        password: str,
        device_type: str,
        connection_type: str = "ssh",
        port: Optional[int] = None,
        enable_password: Optional[str] = None,
        timeout: Optional[int] = None,
        use_basic_commands: bool = True,
        commands: Optional[List[str]] = None
    ) -> Dict:
        """
        Execute commands on a single device
        
        Args:
            ip: Device IP address
            username: Login username
            password: Login password
            device_type: Type of device
            connection_type: 'ssh' or 'telnet' (default: 'ssh')
            port: Custom port number (optional)
            enable_password: Enable/privileged mode password (optional)
            timeout: Connection timeout in seconds (optional)
            use_basic_commands: Use predefined commands (default: True)
            commands: Custom commands list (optional)
            
        Returns:
            Dict with success status, result_id, results, and timestamp
        """
        data = {
            'ip_address': ip,
            'username': username,
            'password': password,
            'device_type': device_type,
            'connection_type': connection_type,
            'use_basic_commands': use_basic_commands
        }
        
        if port:
            data['port'] = port
        if enable_password:
            data['enable_password'] = enable_password
        if timeout:
            data['timeout'] = timeout
        if commands:
            data['commands'] = commands
        
        response = self._request('POST', '/execute', data=data)
        if not response.get('success'):
            raise NetOpsAPIError(response.get('error', 'Command execution failed'))
        return response
    
    def execute_device(self, device: DeviceConfig, commands: Optional[List[str]] = None) -> Dict:
        """
        Execute commands using a DeviceConfig object
        
        Args:
            device: DeviceConfig object with device details
            commands: Custom commands list (optional)
            
        Returns:
            Dict with execution results
        """
        return self.execute(
            ip=device.ip_address,
            username=device.username,
            password=device.password,
            device_type=device.device_type,
            connection_type=device.connection_type,
            port=device.port,
            enable_password=device.enable_password,
            timeout=device.timeout,
            use_basic_commands=commands is None,
            commands=commands
        )
    
    def batch_execute(
        self,
        devices: List[Union[DeviceConfig, Dict]],
        use_basic_commands: bool = True,
        commands: Optional[List[str]] = None
    ) -> Dict:
        """
        Execute commands on multiple devices
        
        Args:
            devices: List of DeviceConfig objects or device dictionaries
            use_basic_commands: Use predefined commands (default: True)
            commands: Custom commands list (optional)
            
        Returns:
            Dict with batch results including total, successful, failed counts
        """
        # Convert DeviceConfig objects to dictionaries
        device_dicts = []
        for device in devices:
            if isinstance(device, DeviceConfig):
                device_dict = {
                    'ip_address': device.ip_address,
                    'username': device.username,
                    'password': device.password,
                    'device_type': device.device_type,
                    'connection_type': device.connection_type
                }
                if device.name:
                    device_dict['name'] = device.name
                if device.port:
                    device_dict['port'] = device.port
                if device.enable_password:
                    device_dict['enable_password'] = device.enable_password
                if device.timeout:
                    device_dict['timeout'] = device.timeout
                device_dicts.append(device_dict)
            else:
                device_dicts.append(device)
        
        data = {
            'devices': device_dicts,
            'use_basic_commands': use_basic_commands,
            'commands': commands or []
        }
        
        response = self._request('POST', '/batch-execute', data=data)
        if not response.get('success'):
            raise NetOpsAPIError(response.get('error', 'Batch execution failed'))
        return response
    
    def get_results(self, result_id: str) -> Dict:
        """
        Get cached results by ID
        
        Args:
            result_id: Result ID from previous execution
            
        Returns:
            Dict with cached result data
        """
        response = self._request('GET', f'/results/{result_id}')
        if not response.get('success'):
            raise NetOpsAPIError(response.get('error', 'Result not found'))
        return response.get('data', {})
    
    def download_results(self, result_id: str, filename: str):
        """
        Download results to a JSON file
        
        Args:
            result_id: Result ID from previous execution
            filename: Output filename
        """
        results = self.get_results(result_id)
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)


# Example usage and test suite
if __name__ == "__main__":
    import os
    
    print("NetOps Command Center - Python SDK Test")
    print("=" * 60)
    
    # Initialize client
    client = NetOpsClient("http://localhost:5000")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    if client.is_healthy():
        print("   ✓ API is healthy")
    else:
        print("   ✗ API is not responding")
        exit(1)
    
    # Test 2: Get device types
    print("\n2. Getting device types...")
    try:
        device_types = client.get_device_types()
        print(f"   ✓ Found {len(device_types)} device types:")
        for dt in device_types:
            print(f"      - {dt['label']} ({dt['value']})")
    except NetOpsAPIError as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Get basic commands
    print("\n3. Getting basic commands for brocade_icx...")
    try:
        commands = client.get_basic_commands('brocade_icx')
        print(f"   ✓ Found {len(commands)} commands:")
        for cmd in commands[:3]:  # Show first 3
            print(f"      - {cmd}")
    except NetOpsAPIError as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Execute command (requires real device)
    print("\n4. Execute command example (not running - requires real device)")
    print("""
    Example code:
    
    result = client.execute(
        ip="192.168.1.1",
        username=os.getenv("TACACS_USER"),
        password=os.getenv("TACACS_PASS"),
        device_type="brocade_icx",
        use_basic_commands=True
    )
    
    if result['success']:
        print(f"Success! Result ID: {result['result_id']}")
        for command, output in result['results'].items():
            print(f"\\nCommand: {command}")
            print(output[:200])  # First 200 chars
    """)
    
    # Test 5: Batch execution example
    print("\n5. Batch execution example (not running - requires real devices)")
    print("""
    Example code:
    
    devices = [
        DeviceConfig(
            ip_address="192.168.1.1",
            username=os.getenv("TACACS_USER"),
            password=os.getenv("TACACS_PASS"),
            device_type="brocade_icx",
            name="Core Switch 1"
        ),
        DeviceConfig(
            ip_address="192.168.1.2",
            username=os.getenv("TACACS_USER"),
            password=os.getenv("TACACS_PASS"),
            device_type="ciena",
            name="Edge Router 1"
        )
    ]
    
    results = client.batch_execute(devices)
    print(f"Batch complete: {results['successful']}/{results['total']} successful")
    """)
    
    print("\n" + "=" * 60)
    print("SDK test complete!")
    print("\nFor more examples, see: API_INTEGRATION.md")
