import os
import django
import sys
import asyncio
import json
import socket
import websockets
from pathlib import Path

# 1. Setup Django Environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simpleblog.settings')

# Mock AI dependencies to prevent import errors during diagnostics
from unittest.mock import MagicMock
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
sys.modules["google.genai.types"] = MagicMock()

try:
    django.setup()
    from django.conf import settings
    from channels.layers import get_channel_layer
    print("✅ Django setup successful.")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

async def test_network_layer():
    print("\n--- [1/4] Network Layer ---")
    host = "localhost"
    port = 8000
    try:
        with socket.create_connection((host, port), timeout=3):
            print(f"✅ OK: Port {port} is OPEN.")
    except Exception as e:
        print(f"❌ FAIL: Could not connect to port {port}. Is Daphne running? Error: {e}")

async def test_redis_layer():
    print("\n--- [2/4] Channel Layer (Redis) ---")
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            print("❌ FAIL: No CHANNEL_LAYERS configured in settings.py.")
            return

        print(f"Using Backend: {settings.CHANNEL_LAYERS['default']['BACKEND']}")
        
        # Test sending/receiving internal message
        channel_name = await channel_layer.new_channel()
        await channel_layer.send(channel_name, {"type": "test.message", "text": "PING"})
        message = await channel_layer.receive(channel_name)
        
        if message and message.get("text") == "PING":
            print("✅ OK: Channel layer is healthy and Redis is responding.")
        else:
            print(f"❌ FAIL: Unexpected message received: {message}")
    except Exception as e:
        print(f"❌ FAIL: Channel layer error (usually Redis is down): {e}")

async def test_handshake(token):
    print("\n--- [3/4] Handshake & Routing ---")
    # Base URL: ws://localhost:8000/ws/chat/test_room/?token=...
    ws_url = f"ws://localhost:8000/ws/chat/test_room/?token={token}"
    print(f"Connecting to: {ws_url}")
    
    try:
        async with websockets.connect(ws_url, timeout=5) as ws:
            print("✅ OK: Handshake SUCCESSFUL!")
            
            # Send sample message
            print("\n--- [4/4] Message Passing ---")
            payload = {"message": "Diagnostic Ping", "sender": 0}
            await ws.send(json.dumps(payload))
            print("💾 Sent message to server. Waiting for broadcast...")
            
            try:
                # Most chat consumers broadcast the message back
                reply = await asyncio.wait_for(ws.recv(), timeout=5)
                print(f"📥 SUCCESS: Received broadcast: {reply}")
            except asyncio.TimeoutError:
                print("⚠️  TIMEOUT: No message received back. Check if your consumer broadcasts to the group.")
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ FAIL: Handshake rejected with Status {e.status_code}.")
        if e.status_code == 403:
            print("   => JWT TOKEN is likely invalid or expired.")
    except Exception as e:
        print(f"❌ FAIL: Connection error: {e}")

async def main():
    print("========================================")
    print("   KCESI WebSocket Diagnostic Tool      ")
    print("========================================")
    
    await test_network_layer()
    await test_redis_layer()
    
    print("\n[!] To test Step 3 (Handshake), you need a valid JWT Token.")
    token = input("Enter a valid access token (or press Enter to skip): ").strip()
    
    if token:
        await test_handshake(token)
    else:
        print("\nSkipping handshake test. Provide a token later to test full authentication.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
