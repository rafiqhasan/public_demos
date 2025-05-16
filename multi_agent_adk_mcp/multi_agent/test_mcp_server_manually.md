# MCP Server Testing Guide

## Step-by-Step Process for Testing an MCP Server with cURL

### 1. Start the MCP Server
First, ensure your MCP server is running:
```bash
python mcp_server.py
```

### 2. Get a Session ID
Connect to the SSE endpoint to get a session ID:
```bash
curl -N -H "Accept: text/event-stream" "http://localhost:8000/sse"
```
This will return:
```
event: endpoint
data: /messages/?session_id=<your_session_id>
```

### 3. Initialize the Session
Send an initialization request using the session ID:
```bash
curl -X POST "http://localhost:8000/messages/?session_id=<your_session_id>" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "curl-client",
        "version": "1.0.0"
      }
    }
  }'
```

### 4. Send the "initialized" Notification
This is a required step in the MCP protocol lifecycle:
```bash
curl -X POST "http://localhost:8000/messages/?session_id=<your_session_id>" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'
```

### 5. List Available Tools (Optional)
Verify which tools are available:
```bash
curl -X POST "http://localhost:8000/messages/?session_id=<your_session_id>" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":2}'
```

### 6. Call the google_search Tool
```bash
curl -X POST "http://localhost:8000/messages/?session_id=<your_session_id>" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "google_search",
      "arguments": {
        "query": "latest technology news"
      }
    }
  }'
```

### 7. Call the flight_booking_tool
```bash
curl -X POST "http://localhost:8000/messages/?session_id=<your_session_id>" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "flight_booking_tool",
      "arguments": {
        "from_location": "New York",
        "to_location": "San Francisco",
        "passenger_name": "John Doe",
        "date": "2025-06-01"
      }
    }
  }'
```

## Notes:
- The MCP protocol follows a specific lifecycle: initialize → initialized notification → tool calls
- Always use the same session ID for all requests in a session
- For persistent monitoring of responses, keep an SSE connection open in a separate terminal:
  ```bash
  curl -N -H "Accept: text/event-stream" "http://localhost:8000/messages/?session_id=<your_session_id>"
  ```
- Each tool has specific required parameters that must be provided in the "arguments" object
- The server returns responses in SSE format with events that contain JSON-RPC responses

## Reference:
- MCP Protocol Specification: https://modelcontextprotocol.io/specification/draft/basic/lifecycle
- FastMCP Documentation: https://github.com/microsoft/modelcontextprotocol/tree/main/python/mcp/server/fastmcp