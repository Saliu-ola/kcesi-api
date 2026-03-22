import os
import django
import sys
import asyncio
import json
import socket
import platform
import subprocess
from pathlib import Path

# 1. Setup Django Environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simpleblog.settings')

# Mock AI dependencies to prevent import errors
from unittest.mock import MagicMock
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
sys.modules["google.genai.types"] = MagicMock()

def print_header(text):
    print(f"\n{'='*60}\n{text.center(60)}\n{'='*60}")

def check_env():
    print_header("SYSTEM ENVIRONMENT")
    print(f"OS: {platform.system()} {platform.release()} ({platform.version()})")
    print(f"Python: {sys.version}")
    print(f"Working Dir: {os.getcwd()}")
    
    print("\n--- Installed Packages (Relevant) ---")
    try:
        # Check specific packages directly
        for pkg in ['channels', 'channels-redis', 'daphne', 'redis', 'websockets', 'twisted']:
            try:
                import importlib.metadata
                ver = importlib.metadata.version(pkg)
                print(f"✅ {pkg.ljust(15)} : {ver}")
            except:
                print(f"❌ {pkg.ljust(15)} : NOT INSTALLED")
    except:
        # Fallback if importlib.metadata fails
        print("Checking via pip...")
        subprocess.run(["pip", "show", "channels", "channels-redis", "daphne", "redis"], capture_output=True)

async def test_network():
    print_header("NETWORK LAYER")
    host = "localhost"
    port = 8000
    try:
        with socket.create_connection((host, port), timeout=3):
            print(f"✅ OK: Port {port} is OPEN and responding.")
    except Exception as e:
        print(f"❌ FAIL: Port {port} is CLOSED or unreachable. Error: {e}")

async def test_django_redis():
    print_header("DJANGO & REDIS LAYER")
    try:
        django.setup()
        from django.conf import settings
        from channels.layers import get_channel_layer
        
        print(f"✅ Django setup successful. Application: {settings.ASGI_APPLICATION}")
        
        channel_layer = get_channel_layer()
        if not channel_layer:
            print("❌ FAIL: No CHANNEL_LAYERS configured.")
            return

        print(f"Backend: {settings.CHANNEL_LAYERS['default']['BACKEND']}")
        
        try:
            # Internal Ping-Pong
            channel_name = await channel_layer.new_channel()
            await channel_layer.send(channel_name, {"type": "test.message", "text": "PING"})
            message = await channel_layer.receive(channel_name)
            if message and message.get("text") == "PING":
                print("✅ OK: Redis Channel Layer is working correctly.")
            else:
                print(f"❌ FAIL: Received junk from Redis: {message}")
        except Exception as e:
            print(f"❌ FAIL: Channel layer error (is Redis running?): {e}")
            
    except Exception as e:
        print(f"❌ FAIL: Django/Settings error: {e}")

async def test_ws_client(token):
    print_header("WEBSOCKET CLIENT TEST")
    import websockets
    ws_url = f"ws://localhost:8000/ws/chat/test_room/?token={token}"
    print(f"Connecting to: {ws_url}")
    try:
        async with websockets.connect(ws_url, timeout=5) as ws:
            print("✅ OK: WS Handshake Success!")
            await ws.send(json.dumps({"message": "Diagnostic", "sender": 0}))
            reply = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"📥 Received broadcast: {reply}")
    except Exception as e:
        print(f"❌ FAIL: WebSocket connection failed: {e}")

async def main():
    check_env()
    await test_network()
    await test_django_redis()
    
    print("\n[!] Handshake check needs a valid TOKEN.")
    token = input("Enter Token (or Enter to finish): ").strip()
    if token:
        await test_ws_client(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\nCRITICAL ERROR IN SCRIPT: {e}")
