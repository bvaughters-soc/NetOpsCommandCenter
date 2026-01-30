# NetOps Command Center - Web Interface

A beautiful, modern web-based interface for managing network devices across your ISP infrastructure. Features a Flask REST API backend with a stunning, cyberpunk-inspired frontend.

![NetOps Command Center](https://img.shields.io/badge/Status-Production%20Ready-success)

## Features

✨ **Stunning UI** - Cyberpunk-inspired design with gradient accents and smooth animations
🚀 **REST API Backend** - Flask-powered API for device management
🔐 **TACACS+ Support** - Full support for TACACS authentication with enable mode
📊 **Batch Operations** - Execute commands across multiple devices simultaneously
📜 **Execution History** - Track all command executions in the browser
🎨 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile

## Quick Start

### Installation

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Start the API Server**
```bash
python3 api_server.py
```

3. **Access the Web Interface**
Open your browser and navigate to:
```
http://localhost:5000
```

That's it! The server will automatically serve both the API and the web interface.

## Usage

### Single Device Operations

1. Navigate to the **Single Device** tab
2. Enter device connection details:
   - IP Address
   - Device Type (Ciena, Brocade, Alcatel)
   - TACACS credentials
   - Optional: Enable password for privileged mode
3. Choose to use basic commands or enter custom commands
4. Click **Execute Commands**
5. View results in real-time

### Batch Operations

1. Navigate to the **Batch Operations** tab
2. Enter JSON configuration with multiple devices
3. Click **Load Template** for an example configuration
4. Choose basic or custom commands
5. Click **Execute Batch**
6. Monitor progress for each device

### Viewing History

Navigate to the **History** tab to see all recent command executions with timestamps and status.

## API Documentation

### Endpoints

#### `GET /api/health`
Health check endpoint
```json
{
  "status": "healthy",
  "timestamp": "2025-01-28T10:30:00",
  "cached_results": 5
}
```

#### `GET /api/device-types`
Get list of supported device types
```json
{
  "success": true,
  "device_types": [
    {"value": "ciena", "label": "Ciena"},
    {"value": "brocade_icx", "label": "Brocade Icx"}
  ]
}
```

#### `POST /api/execute`
Execute commands on a single device

**Request:**
```json
{
  "ip_address": "192.168.1.1",
  "username": "tacacs_user",
  "password": "tacacs_pass",
  "enable_password": "enable_pass",
  "device_type": "brocade_icx",
  "connection_type": "ssh",
  "port": 22,
  "timeout": 30,
  "use_basic_commands": true,
  "commands": []
}
```

**Response:**
```json
{
  "success": true,
  "result_id": "192.168.1.1_1234567890",
  "results": {
    "show version": "Output here...",
    "show running-config": "Output here..."
  },
  "timestamp": "2025-01-28T10:30:00"
}
```

#### `POST /api/batch-execute`
Execute commands on multiple devices

**Request:**
```json
{
  "devices": [
    {
      "name": "Switch 1",
      "ip_address": "192.168.1.10",
      "username": "admin",
      "password": "password",
      "device_type": "brocade_icx",
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
  "batch_id": "batch_1234567890",
  "total": 5,
  "successful": 4,
  "failed": 1,
  "results": [...],
  "timestamp": "2025-01-28T10:30:00"
}
```

#### `GET /api/results/<result_id>`
Retrieve cached results by ID

#### `GET /api/results/<result_id>/download`
Download results as JSON file

## Architecture

```
┌─────────────────┐
│   Web Browser   │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/JSON
         │
┌────────▼────────┐
│  Flask API      │
│  (api_server.py)│
└────────┬────────┘
         │
┌────────▼────────┐
│  Device Manager │
│  (Python Core)  │
└────────┬────────┘
         │ SSH/Telnet
         │
┌────────▼────────┐
│ Network Devices │
│ (Ciena, Brocade │
│  Alcatel, etc.) │
└─────────────────┘
```

## Frontend Design

The web interface features a distinctive cyberpunk aesthetic:

- **Typography**: Outfit (display) + JetBrains Mono (code)
- **Color Scheme**: Dark theme with cyan/magenta gradients
- **Animations**: Smooth page transitions and micro-interactions
- **Layout**: Card-based design with responsive grid
- **Effects**: Animated background gradients, hover states, and loading indicators

## Security Considerations

⚠️ **Important for Production Deployment:**

1. **HTTPS Only** - Always use HTTPS in production
2. **Authentication** - Add user authentication to the API
3. **Rate Limiting** - Implement rate limiting on API endpoints
4. **CORS** - Configure CORS for your specific domain
5. **Secrets Management** - Never hardcode credentials
6. **Input Validation** - API validates all inputs
7. **Session Management** - Consider implementing sessions for multi-user environments

### Recommended Production Setup

```python
# Use environment variables for sensitive config
export FLASK_SECRET_KEY="your-secret-key"
export ALLOWED_ORIGINS="https://your-domain.com"

# Run with gunicorn in production
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

## Customization

### Changing the Color Scheme

Edit the CSS variables in `static/index.html`:

```css
:root {
    --accent-cyan: #00f5ff;      /* Primary accent */
    --accent-magenta: #ff00aa;   /* Secondary accent */
    --accent-orange: #ff6b35;    /* Tertiary accent */
}
```

### Adding New Device Types

1. Update `network_device_manager.py` with new device type
2. Add commands to `DeviceCommands.BASIC_COMMANDS`
3. The frontend will automatically populate new device types

## Development

### Project Structure

```
.
├── api_server.py              # Flask API backend
├── network_device_manager.py  # Core device management library
├── static/
│   └── index.html            # Web interface
├── requirements.txt          # Python dependencies
└── README_WEB.md            # This file
```

### Running in Development Mode

```bash
# The server runs in debug mode by default
python3 api_server.py

# Access at http://localhost:5000
```

### API Testing with curl

```bash
# Health check
curl http://localhost:5000/api/health

# Execute command
curl -X POST http://localhost:5000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "192.168.1.1",
    "username": "admin",
    "password": "password",
    "device_type": "ciena",
    "connection_type": "ssh",
    "use_basic_commands": true
  }'
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### CORS Errors
Make sure Flask-CORS is installed and the API server is running.

### Connection Timeouts
- Increase timeout value in the form
- Check network connectivity to devices
- Verify firewall rules

### Authentication Failures
- Verify TACACS credentials are correct
- Check if enable password is required
- Review device logs for auth failures

## Browser Compatibility

- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ⚠️ IE11 (Limited support)

## Performance

- **Concurrent Requests**: Handles multiple simultaneous device connections
- **Response Time**: Typically 2-10 seconds per device depending on network latency
- **Caching**: Results cached in-memory (lost on server restart)
- **Scalability**: For large deployments, consider implementing a database backend

## Future Enhancements

- [ ] User authentication and authorization
- [ ] Persistent result storage (database)
- [ ] Scheduled command execution
- [ ] Real-time WebSocket updates
- [ ] Command templates library
- [ ] Device grouping and tagging
- [ ] Export results to PDF/Excel
- [ ] Audit logging
- [ ] Multi-tenancy support

## License

This tool is provided as-is for ISP network management purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API logs with verbose mode
3. Test individual components (CLI, API, frontend)
4. Verify network connectivity

## Credits

Built with:
- Flask - Web framework
- Paramiko - SSH library
- Modern CSS - Animations and gradients
- JetBrains Mono & Outfit - Typography
