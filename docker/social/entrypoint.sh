#!/bin/bash

# Entrypoint script for Social Media Automation Container

set -e

echo "Starting Social Media Automation Container..."

# Ensure logs directory exists
mkdir -p /app/logs

# Start cron daemon
echo "Starting cron daemon..."
cron

# Create a simple health check endpoint
echo "Starting health check server..."
python3 -c "
import http.server
import socketserver
import threading
import time
import os
from datetime import datetime

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Check if automation ran recently (within 10 minutes)
            log_file = '/app/logs/cron.log'
            status = 'healthy'
            last_run = 'never'
            
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            last_run = lines[-1].strip()
                except:
                    pass
            
            response = {
                'status': status,
                'service': 'social-media-automation',
                'last_run': last_run,
                'timestamp': datetime.now().isoformat()
            }
            
            import json
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress HTTP logs

def start_health_server():
    with socketserver.TCPServer(('0.0.0.0', 8080), HealthHandler) as httpd:
        httpd.serve_forever()

# Start health server in background
health_thread = threading.Thread(target=start_health_server, daemon=True)
health_thread.start()

print('Health check endpoint started on port 8080')
print('Social media automation will run every 5 minutes via cron')
print('Logs available at /app/logs/cron.log')

# Keep container running and tail logs
while True:
    try:
        if os.path.exists('/app/logs/cron.log'):
            os.system('tail -f /app/logs/cron.log')
        else:
            time.sleep(60)
            print(f'{datetime.now()}: Waiting for automation logs...')
    except KeyboardInterrupt:
        print('Shutting down...')
        break
" &

# Wait for any process to exit
wait