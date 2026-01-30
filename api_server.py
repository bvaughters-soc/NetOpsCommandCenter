#!/usr/bin/env python3
"""
Flask API Backend for Network Device Manager
Provides REST API endpoints for device management
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
from typing import Dict, List
import traceback

from network_device_manager import (
    DeviceManager, DeviceCredentials, DeviceType, 
    ConnectionType, DeviceCommands
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for frontend access

# Device manager instance
device_manager = DeviceManager()

# Store results temporarily (in production, use a database)
results_cache = {}


@app.route('/')
def index():
    """Serve the main HTML interface"""
    return send_from_directory('static', 'index.html')


@app.route('/api/device-types', methods=['GET'])
def get_device_types():
    """Get list of supported device types"""
    try:
        device_types = [
            {
                'value': dt.value,
                'label': dt.value.replace('_', ' ').title()
            }
            for dt in DeviceType
        ]
        return jsonify({
            'success': True,
            'device_types': device_types
        })
    except Exception as e:
        logger.error(f"Error getting device types: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/basic-commands', methods=['POST'])
def get_basic_commands():
    """Get basic commands for a specific device type"""
    try:
        data = request.json
        device_type = DeviceType(data.get('device_type'))
        
        commands = DeviceCommands.get_basic_commands(device_type)
        
        return jsonify({
            'success': True,
            'commands': commands
        })
    except Exception as e:
        logger.error(f"Error getting basic commands: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/execute', methods=['POST'])
def execute_commands():
    """Execute commands on a device"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['ip_address', 'username', 'password', 'device_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create credentials
        credentials = DeviceCredentials(
            ip_address=data['ip_address'],
            username=data['username'],
            password=data['password'],
            enable_password=data.get('enable_password'),
            port=data.get('port'),
            device_type=DeviceType(data['device_type']),
            connection_type=ConnectionType(data.get('connection_type', 'ssh')),
            timeout=data.get('timeout', 30)
        )
        
        # Determine commands to execute
        use_basic = data.get('use_basic_commands', False)
        custom_commands = data.get('commands', [])
        
        if not use_basic and not custom_commands:
            return jsonify({
                'success': False,
                'error': 'Must specify either use_basic_commands=true or provide custom commands'
            }), 400
        
        # Execute commands
        logger.info(f"Executing commands on {credentials.ip_address}")
        results = device_manager.execute_commands(
            credentials,
            commands=custom_commands if custom_commands else None,
            use_basic_commands=use_basic
        )
        
        # Store results with unique ID
        result_id = f"{credentials.ip_address}_{datetime.now().timestamp()}"
        results_cache[result_id] = {
            'timestamp': datetime.now().isoformat(),
            'device': {
                'ip_address': credentials.ip_address,
                'device_type': credentials.device_type.value
            },
            'results': results
        }
        
        return jsonify({
            'success': True,
            'result_id': result_id,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error executing commands: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'details': traceback.format_exc()
        }), 500


@app.route('/api/batch-execute', methods=['POST'])
def batch_execute():
    """Execute commands on multiple devices"""
    try:
        data = request.json
        devices = data.get('devices', [])
        use_basic = data.get('use_basic_commands', False)
        custom_commands = data.get('commands', [])
        
        if not devices:
            return jsonify({
                'success': False,
                'error': 'No devices provided'
            }), 400
        
        results = []
        
        for device_config in devices:
            try:
                # Create credentials
                credentials = DeviceCredentials(
                    ip_address=device_config['ip_address'],
                    username=device_config['username'],
                    password=device_config['password'],
                    enable_password=device_config.get('enable_password'),
                    port=device_config.get('port'),
                    device_type=DeviceType(device_config['device_type']),
                    connection_type=ConnectionType(device_config.get('connection_type', 'ssh')),
                    timeout=device_config.get('timeout', 30)
                )
                
                # Execute commands
                device_results = device_manager.execute_commands(
                    credentials,
                    commands=custom_commands if custom_commands else None,
                    use_basic_commands=use_basic
                )
                
                results.append({
                    'device_name': device_config.get('name', credentials.ip_address),
                    'ip_address': credentials.ip_address,
                    'status': 'success',
                    'results': device_results
                })
                
            except Exception as e:
                results.append({
                    'device_name': device_config.get('name', device_config['ip_address']),
                    'ip_address': device_config['ip_address'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Store batch results
        batch_id = f"batch_{datetime.now().timestamp()}"
        results_cache[batch_id] = {
            'timestamp': datetime.now().isoformat(),
            'type': 'batch',
            'results': results
        }
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        
        return jsonify({
            'success': True,
            'batch_id': batch_id,
            'total': len(results),
            'successful': success_count,
            'failed': len(results) - success_count,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in batch execution: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/results/<result_id>', methods=['GET'])
def get_results(result_id):
    """Retrieve cached results by ID"""
    if result_id in results_cache:
        return jsonify({
            'success': True,
            'data': results_cache[result_id]
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Result not found'
        }), 404


@app.route('/api/results/<result_id>/download', methods=['GET'])
def download_results(result_id):
    """Download results as JSON file"""
    if result_id in results_cache:
        return jsonify(results_cache[result_id])
    else:
        return jsonify({
            'success': False,
            'error': 'Result not found'
        }), 404


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cached_results': len(results_cache)
    })


if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Run the Flask app
    print("=" * 60)
    print("Network Device Manager API Server")
    print("=" * 60)
    print("Server starting on http://0.0.0.0:5000")
    print("API Documentation:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/device-types        - List supported devices")
    print("  POST /api/basic-commands      - Get basic commands for device")
    print("  POST /api/execute             - Execute commands on device")
    print("  POST /api/batch-execute       - Execute on multiple devices")
    print("  GET  /api/results/<id>        - Get cached results")
    print("=" * 60)
    
    # Check if running in production
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    app.run(
        debug=not is_production,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
