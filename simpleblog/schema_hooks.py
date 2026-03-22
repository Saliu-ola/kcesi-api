def postprocess_schema_hooks(result, generator, request, public):
    """
    Post-processing hook for drf-spectacular to add WebSocket documentation.
    """
    
    # Add WebSocket paths to the 'paths' section
    websocket_paths = {
        "/ws/chat/{room_name}/": {
            "get": {
                "tags": ["Websockets"],
                "summary": "Real-time Chat WebSocket",
                "description": (
                    "Connect to this endpoint for real-time messaging, comments, and replies.\n\n"
                    "**Authentication**: Must provide a JWT token in the query string: `?token=YOUR_JWT_TOKEN`.\n\n"
                    "**Incoming Message Format (JSON)**:\n"
                    "```json\n"
                    "{\n"
                    "  \"message\": \"string\",\n"
                    "  \"sender\": \"number (User ID)\",\n"
                    "  \"receiver\": \"number (User ID)\",\n"
                    "  \"content_type\": \"string\",\n"
                    "  \"organization\": \"number (Org ID)\",\n"
                    "  \"group\": \"number (Group ID, optional)\",\n"
                    "  \"resource\": \"number (Resource ID, optional)\",\n"
                    "  \"unique_identifier\": \"uuid\",\n"
                    "  \"score\": \"number\"\n"
                    "}\n"
                    "```"
                ),
                "parameters": [
                    {
                        "name": "room_name",
                        "in": "path",
                        "required": True,
                        "description": "Unique identifier for the chat room.",
                        "schema": {"type": "string"},
                    },
                    {
                        "name": "token",
                        "in": "query",
                        "required": True,
                        "description": "JWT Access Token for authentication.",
                        "schema": {"type": "string"},
                    },
                ],
                "responses": {"101": {"description": "Switching Protocols (Handshake Successful)"}},
            }
        },
        "/ws/forums/comments/{room_name}/": {
            "get": {
                "tags": ["Websockets"],
                "summary": "Forum Comments WebSocket",
                "description": "Real-time updates for forum comments.",
                "parameters": [
                    {"name": "room_name", "in": "path", "required": True, "schema": {"type": "string"}},
                    {"name": "token", "in": "query", "required": True, "schema": {"type": "string"}},
                ],
                "responses": {"101": {"description": "Switching Protocols"}},
            }
        },
        "/ws/blogs/comments/{room_name}/": {
            "get": {
                "tags": ["Websockets"],
                "summary": "Blog Comments WebSocket",
                "description": "Real-time updates for blog comments.",
                "parameters": [
                    {"name": "room_name", "in": "path", "required": True, "schema": {"type": "string"}},
                    {"name": "token", "in": "query", "required": True, "schema": {"type": "string"}},
                ],
                "responses": {"101": {"description": "Switching Protocols"}},
            }
        },
    }

    result["paths"].update(websocket_paths)
    return result
