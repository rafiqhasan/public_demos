#!/bin/bash

# Kill any existing processes on ports 8000 and 8001
echo "Cleaning up existing processes on ports 8000 and 8001..."

# Method 1: Using fuser (most reliable)
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 8001/tcp 2>/dev/null || true

# Method 2: Backup using netstat and awk (if fuser not available)
if command -v netstat >/dev/null 2>&1; then
    netstat -tulpn 2>/dev/null | grep ':8000 ' | awk '{print $7}' | cut -d'/' -f1 | xargs -r kill -9 2>/dev/null || true
    netstat -tulpn 2>/dev/null | grep ':8001 ' | awk '{print $7}' | cut -d'/' -f1 | xargs -r kill -9 2>/dev/null || true
fi

# Method 3: Kill specific Python processes (if you know they're Python)
pkill -f "mcp_server_google.py" 2>/dev/null || true
pkill -f "mcp_server_travel.py" 2>/dev/null || true

# Wait a moment for processes to fully terminate
sleep 2

echo "Starting MCP servers..."
python mcp_server_google.py &
python mcp_server_travel.py &

echo "MCP servers started on ports 8000 and 8001"