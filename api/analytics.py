#!/usr/bin/env python3
"""
Analytics API Endpoint for PWA - Privacy-Focused No-Op Version
Returns success responses without collecting any user data
"""

import json
import os
from datetime import datetime

def handle_analytics_post():
    """Handle POST request - return success without storing data"""
    # Read and discard any posted data without storing it
    content_length = int(os.environ.get('CONTENT_LENGTH', 0))
    if content_length > 0:
        sys.stdin.read(content_length)  # Discard the data
    
    # Return success response without storing any data
    response = {
        'success': True,
        'message': 'Request acknowledged (no data stored)',
        'timestamp': datetime.now().isoformat()
    }
    
    print("Content-Type: application/json")
    print()
    print(json.dumps(response))

def handle_analytics_get():
    """Handle GET request - return empty analytics data"""
    response = {
        'success': True,
        'data': {
            'total_events': 0,
            'recent_events': [],
            'message': 'No analytics data collected (privacy-focused)'
        },
        'timestamp': datetime.now().isoformat()
    }
    
    print("Content-Type: application/json")
    print()
    print(json.dumps(response))

if __name__ == "__main__":
    import sys
    request_method = os.environ.get('REQUEST_METHOD', 'GET')
    
    if request_method == 'POST':
        handle_analytics_post()
    else:
        handle_analytics_get()