#!/usr/bin/env python3
"""
Simple HTTP API Server for Search Functionality
Provides a REST endpoint for the search backend
"""

import json
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

# Add src to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from search_backend import SearchBackend

# Import configuration
try:
    from utils.config import config
except ImportError:
    config = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SearchAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for search API"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        # CORS headers for development
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        if parsed_path.path == '/api/search':
            self.handle_search(parsed_path)
        elif parsed_path.path == '/api/suggestions':
            self.handle_suggestions(parsed_path)
        else:
            self.send_error(404, 'Endpoint not found')
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_search(self, parsed_path):
        """Handle search endpoint"""
        query_params = parse_qs(parsed_path.query)
        
        # Extract parameters with config defaults
        query = query_params.get('q', [''])[0]
        default_limit = config.get('limits.search_results_per_page', 20) if config else 20
        limit = int(query_params.get('limit', [str(default_limit)])[0])
        offset = int(query_params.get('offset', ['0'])[0])
        
        # Perform search
        search_backend = SearchBackend()
        results = search_backend.search_all(query, limit, offset)
        
        # Send response
        self.end_headers()
        self.wfile.write(json.dumps(results, indent=2).encode())
    
    def handle_suggestions(self, parsed_path):
        """Handle suggestions endpoint"""
        query_params = parse_qs(parsed_path.query)
        
        # Extract parameters
        query = query_params.get('q', [''])[0]
        limit = int(query_params.get('limit', ['5'])[0])
        
        # Get suggestions
        search_backend = SearchBackend()
        suggestions = search_backend.get_suggestions(query, limit)
        
        # Send response
        self.end_headers()
        self.wfile.write(json.dumps({
            'query': query,
            'suggestions': suggestions
        }, indent=2).encode())
    
    def log_message(self, format, *args):
        """Override to use logger instead of stderr"""
        logger.info("%s - - [%s] %s\n" %
                    (self.client_address[0],
                     self.log_date_time_string(),
                     format % args))


def run_server(port=None):
    """Run the search API server"""
    # Use config port if available, otherwise default to 8080
    if port is None:
        port = config.get('server.port', 8080) if config else 8080
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, SearchAPIHandler)
    
    logger.info(f"Starting search API server on port {port}")
    logger.info(f"Access the API at: http://localhost:{port}/api/search?q=your_query")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        httpd.shutdown()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Search API Server')
    default_port = config.get('server.port', 8080) if config else 8080
    parser.add_argument('--port', type=int, default=default_port,
                        help=f'Port to run the server on (default: {default_port})')
    
    args = parser.parse_args()
    run_server(args.port)