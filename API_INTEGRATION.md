# NetOps Command Center - API Integration Guide

The NetOps Command Center provides a complete REST API for integrating with other systems, automation tools, scripts, and applications.

## Base URL

```
http://localhost:5000/api
```

For remote access:
```
http://YOUR_SERVER_IP:5000/api
```

---

## Authentication

Currently, the API does not require authentication for requests. For production deployment, you should add:
- API key authentication
- JWT tokens
- OAuth 2.0
- Basic Auth

See the [Security Section](#adding-authentication) below for implementation examples.

---

## API Endpoints

### 1. Health Check

**Endpoint:** `GET /api/health`

**Description:** Check if the API is running and healthy

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-29T10:30:00",
  "cached_results": 5
}
```

**Example:**
```bash
curl http://localhost:5000/api/health
```

---

### 2. Get Device Types

**Endpoint:** `GET /api/device-types`

**Description:** Get list of all supported device types

**Response:**
```json
{
  "success": true,
  "device_types": [
    {
      "value": "ciena",
      "label": "Ciena"
    },
    {
      "value": "brocade_icx",
      "label": "Brocade Icx"
    },
    {
      "value": "brocade_ces",
      "label": "Brocade Ces"
    },
    {
      "value": "brocade_fws",
      "label": "Brocade Fws"
    },
    {
      "value": "alcatel_7210",
      "label": "Alcatel 7210"
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:5000/api/device-types
```

---

### 3. Get Basic Commands

**Endpoint:** `POST /api/basic-commands`

**Description:** Get predefined basic commands for a specific device type

**Request Body:**
```json
{
  "device_type": "brocade_icx"
}
```

**Response:**
```json
{
  "success": true,
  "commands": [
    "show version",
    "show running-config",
    "show interface brief",
    "show ip interface brief"
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/basic-commands \
  -H "Content-Type: application/json" \
  -d '{"device_type": "brocade_icx"}'
```

---

### 4. Execute Commands (Single Device)

**Endpoint:** `POST /api/execute`

**Description:** Execute commands on a single network device

**Request Body:**
```json
{
  "ip_address": "192.168.1.1",
  "username": "admin",
  "password": "password",
  "enable_password": "enable_pass",
  "device_type": "brocade_icx",
  "connection_type": "ssh",
  "port": 22,
  "timeout": 30,
  "use_basic_commands": true,
  "commands": []
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ip_address` | string | Yes | Device IP address |
| `username` | string | Yes | Login username |
| `password` | string | Yes | Login password |
| `device_type` | string | Yes | Device type (see device-types) |
| `connection_type` | string | No | "ssh" or "telnet" (default: ssh) |
| `port` | integer | No | Custom port (default: 22 for SSH, 23 for Telnet) |
| `enable_password` | string | No | Enable/privileged mode password |
| `timeout` | integer | No | Connection timeout in seconds (default: 30) |
| `use_basic_commands` | boolean | No | Use predefined commands (default: false) |
| `commands` | array | No | Custom commands to execute |

**Response:**
```json
{
  "success": true,
  "result_id": "192.168.1.1_1706523000.123",
  "results": {
    "show version": "ICX7450-48 Router...",
    "show running-config": "Current configuration..."
  },
  "timestamp": "2025-01-29T10:30:00"
}
```

**Example - Basic Commands:**
```bash
curl -X POST http://localhost:5000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "192.168.1.1",
    "username": "admin",
    "password": "password",
    "device_type": "brocade_icx",
    "use_basic_commands": true
  }'
```

**Example - Custom Commands:**
```bash
curl -X POST http://localhost:5000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "192.168.1.1",
    "username": "admin",
    "password": "password",
    "enable_password": "enable_pass",
    "device_type": "ciena",
    "connection_type": "ssh",
    "commands": ["software show", "system show"]
  }'
```

---

### 5. Execute Batch Commands

**Endpoint:** `POST /api/batch-execute`

**Description:** Execute commands on multiple devices simultaneously

**Request Body:**
```json
{
  "devices": [
    {
      "name": "Core Switch 1",
      "ip_address": "192.168.1.10",
      "username": "admin",
      "password": "password",
      "device_type": "brocade_icx",
      "connection_type": "ssh"
    },
    {
      "name": "Edge Router 1",
      "ip_address": "192.168.1.20",
      "username": "admin",
      "password": "password",
      "enable_password": "enable_pass",
      "device_type": "ciena",
      "connection_type": "ssh"
    }
  ],
  "use_basic_commands": true,
  "commands": []
}
```

**Response:**
```json
{
  "success": true,
  "batch_id": "batch_1706523000.456",
  "total": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "device_name": "Core Switch 1",
      "ip_address": "192.168.1.10",
      "status": "success",
      "results": {
        "show version": "..."
      }
    },
    {
      "device_name": "Edge Router 1",
      "ip_address": "192.168.1.20",
      "status": "success",
      "results": {
        "software show": "..."
      }
    }
  ],
  "timestamp": "2025-01-29T10:30:00"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/batch-execute \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "name": "Switch 1",
        "ip_address": "192.168.1.10",
        "username": "admin",
        "password": "password",
        "device_type": "brocade_icx"
      }
    ],
    "use_basic_commands": true
  }'
```

---

### 6. Get Cached Results

**Endpoint:** `GET /api/results/<result_id>`

**Description:** Retrieve previously executed command results

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2025-01-29T10:30:00",
    "device": {
      "ip_address": "192.168.1.1",
      "device_type": "brocade_icx"
    },
    "results": {
      "show version": "..."
    }
  }
}
```

**Example:**
```bash
curl http://localhost:5000/api/results/192.168.1.1_1706523000.123
```

---

### 7. Download Results

**Endpoint:** `GET /api/results/<result_id>/download`

**Description:** Download results as JSON file

**Example:**
```bash
curl http://localhost:5000/api/results/192.168.1.1_1706523000.123/download \
  -o results.json
```

---

## Integration Examples

### Python Integration

```python
import requests
import json

API_BASE = "http://localhost:5000/api"

# Example 1: Execute commands on a device
def execute_device_commands(ip, username, password, device_type):
    url = f"{API_BASE}/execute"
    
    payload = {
        "ip_address": ip,
        "username": username,
        "password": password,
        "device_type": device_type,
        "use_basic_commands": True
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✓ Success! Result ID: {data['result_id']}")
            return data['results']
        else:
            print(f"✗ Error: {data['error']}")
    else:
        print(f"✗ HTTP Error: {response.status_code}")
    
    return None

# Example 2: Batch execution
def execute_batch(devices):
    url = f"{API_BASE}/batch-execute"
    
    payload = {
        "devices": devices,
        "use_basic_commands": True
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Batch complete: {data['successful']}/{data['total']} successful")
        return data
    
    return None

# Usage
if __name__ == "__main__":
    # Single device
    results = execute_device_commands(
        ip="192.168.1.1",
        username="admin",
        password="password",
        device_type="brocade_icx"
    )
    
    # Batch
    devices = [
        {
            "name": "Switch 1",
            "ip_address": "192.168.1.10",
            "username": "admin",
            "password": "password",
            "device_type": "brocade_icx"
        },
        {
            "name": "Router 1",
            "ip_address": "192.168.1.20",
            "username": "admin",
            "password": "password",
            "device_type": "ciena"
        }
    ]
    
    batch_results = execute_batch(devices)
```

---

### JavaScript/Node.js Integration

```javascript
const axios = require('axios');

const API_BASE = 'http://localhost:5000/api';

// Execute commands on a device
async function executeCommands(deviceConfig) {
    try {
        const response = await axios.post(`${API_BASE}/execute`, {
            ip_address: deviceConfig.ip,
            username: deviceConfig.username,
            password: deviceConfig.password,
            device_type: deviceConfig.type,
            use_basic_commands: true
        });
        
        if (response.data.success) {
            console.log('✓ Success:', response.data.result_id);
            return response.data.results;
        } else {
            console.error('✗ Error:', response.data.error);
        }
    } catch (error) {
        console.error('✗ Request failed:', error.message);
    }
}

// Batch execution
async function executeBatch(devices) {
    try {
        const response = await axios.post(`${API_BASE}/batch-execute`, {
            devices: devices,
            use_basic_commands: true
        });
        
        console.log(`Batch: ${response.data.successful}/${response.data.total} successful`);
        return response.data;
    } catch (error) {
        console.error('✗ Batch failed:', error.message);
    }
}

// Usage
(async () => {
    const results = await executeCommands({
        ip: '192.168.1.1',
        username: 'admin',
        password: 'password',
        type: 'brocade_icx'
    });
    
    console.log(results);
})();
```

---

### PowerShell Integration

```powershell
$API_BASE = "http://localhost:5000/api"

# Execute commands
function Invoke-DeviceCommand {
    param(
        [string]$IpAddress,
        [string]$Username,
        [string]$Password,
        [string]$DeviceType
    )
    
    $body = @{
        ip_address = $IpAddress
        username = $Username
        password = $Password
        device_type = $DeviceType
        use_basic_commands = $true
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$API_BASE/execute" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    if ($response.success) {
        Write-Host "✓ Success: $($response.result_id)"
        return $response.results
    } else {
        Write-Host "✗ Error: $($response.error)"
    }
}

# Usage
$results = Invoke-DeviceCommand `
    -IpAddress "192.168.1.1" `
    -Username "admin" `
    -Password "password" `
    -DeviceType "brocade_icx"

$results | ConvertTo-Json
```

---

### Bash/cURL Integration

```bash
#!/bin/bash
API_BASE="http://localhost:5000/api"

# Execute commands on a device
execute_command() {
    local ip=$1
    local username=$2
    local password=$3
    local device_type=$4
    
    curl -s -X POST "${API_BASE}/execute" \
        -H "Content-Type: application/json" \
        -d "{
            \"ip_address\": \"${ip}\",
            \"username\": \"${username}\",
            \"password\": \"${password}\",
            \"device_type\": \"${device_type}\",
            \"use_basic_commands\": true
        }" | jq .
}

# Batch execution
execute_batch() {
    curl -s -X POST "${API_BASE}/batch-execute" \
        -H "Content-Type: application/json" \
        -d @devices.json | jq .
}

# Usage
execute_command "192.168.1.1" "admin" "password" "brocade_icx"
```

---

### Ansible Integration

```yaml
# playbook.yml
---
- name: Execute network device commands
  hosts: localhost
  tasks:
    - name: Execute commands on Brocade switch
      uri:
        url: "http://localhost:5000/api/execute"
        method: POST
        body_format: json
        body:
          ip_address: "192.168.1.1"
          username: "admin"
          password: "password"
          device_type: "brocade_icx"
          use_basic_commands: true
        status_code: 200
      register: result
    
    - name: Display results
      debug:
        var: result.json.results
```

---

### Webhook Integration

The API can be used as a webhook endpoint for automation:

```python
# Trigger from monitoring system
import requests

def network_device_check(device_ip, device_type):
    """Called by monitoring system when device alert triggers"""
    
    response = requests.post(
        "http://localhost:5000/api/execute",
        json={
            "ip_address": device_ip,
            "username": os.getenv("TACACS_USER"),
            "password": os.getenv("TACACS_PASS"),
            "device_type": device_type,
            "use_basic_commands": True
        }
    )
    
    # Send results to ticketing system, Slack, etc.
    return response.json()
```

---

## Adding Authentication

For production use, add API key authentication:

### Simple API Key Authentication

```python
# In api_server.py
from functools import wraps
from flask import request, jsonify

API_KEY = os.environ.get('API_KEY', 'your-secret-key')

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != API_KEY:
            return jsonify({'success': False, 'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Apply to endpoints
@app.route('/api/execute', methods=['POST'])
@require_api_key
def execute_commands():
    # ... existing code
```

**Usage with API key:**
```bash
curl -X POST http://localhost:5000/api/execute \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "192.168.1.1", ...}'
```

---

## Rate Limiting

Add rate limiting for production:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/execute', methods=['POST'])
@limiter.limit("10 per minute")
def execute_commands():
    # ... existing code
```

---

## CORS Configuration

For cross-origin requests from different domains:

```python
# Already configured in api_server.py
from flask_cors import CORS

# Allow specific origins
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-domain.com", "https://app.your-domain.com"]
    }
})
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message here",
  "details": "Detailed error information (if available)"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad request (missing parameters)
- `401` - Unauthorized (if auth is enabled)
- `404` - Not found
- `500` - Server error

---

## Best Practices

1. **Use environment variables** for credentials
2. **Implement API key authentication** in production
3. **Enable rate limiting** to prevent abuse
4. **Log all API requests** for auditing
5. **Use HTTPS** in production
6. **Validate all inputs** before processing
7. **Handle timeouts** gracefully
8. **Cache results** when appropriate
9. **Monitor API health** regularly
10. **Version your API** for backwards compatibility

---

## Example: Complete Integration Script

```python
#!/usr/bin/env python3
"""
Complete NetOps API Integration Example
"""

import requests
import json
import os
from typing import List, Dict

class NetOpsAPI:
    def __init__(self, base_url: str = "http://localhost:5000/api"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.json().get('status') == 'healthy'
        except:
            return False
    
    def get_device_types(self) -> List[Dict]:
        """Get supported device types"""
        response = self.session.get(f"{self.base_url}/device-types")
        data = response.json()
        return data.get('device_types', [])
    
    def execute_command(self, device_config: Dict) -> Dict:
        """Execute command on single device"""
        response = self.session.post(
            f"{self.base_url}/execute",
            json=device_config
        )
        return response.json()
    
    def batch_execute(self, devices: List[Dict], commands: List[str] = None) -> Dict:
        """Execute commands on multiple devices"""
        payload = {
            "devices": devices,
            "use_basic_commands": commands is None,
            "commands": commands or []
        }
        response = self.session.post(
            f"{self.base_url}/batch-execute",
            json=payload
        )
        return response.json()
    
    def get_results(self, result_id: str) -> Dict:
        """Retrieve cached results"""
        response = self.session.get(f"{self.base_url}/results/{result_id}")
        return response.json()

# Usage example
if __name__ == "__main__":
    api = NetOpsAPI()
    
    # Check health
    if api.health_check():
        print("✓ API is healthy")
    
    # Get device types
    device_types = api.get_device_types()
    print(f"Supported devices: {[dt['label'] for dt in device_types]}")
    
    # Execute single command
    result = api.execute_command({
        "ip_address": "192.168.1.1",
        "username": os.getenv("TACACS_USER"),
        "password": os.getenv("TACACS_PASS"),
        "device_type": "brocade_icx",
        "use_basic_commands": True
    })
    
    if result['success']:
        print(f"✓ Command executed: {result['result_id']}")
    else:
        print(f"✗ Error: {result['error']}")
```

---

## Support

For integration issues or questions:
- Check API health: `GET /api/health`
- Review error messages in response
- Check server logs: `docker-compose logs -f`
- Verify request format matches examples above
