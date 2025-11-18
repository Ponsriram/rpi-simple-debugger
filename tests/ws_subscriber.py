"""
WebSocket subscriber client for rpi-simple-debugger.

This script connects to the /ws endpoint and prints all real-time updates
from GPIO, WiFi, Bluetooth, and system health monitors.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict

try:
    import websockets
except ImportError:
    print("Installing websockets library...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets"])
    import websockets


def format_message(msg: Dict[str, Any]) -> str:
    """Format a message for pretty printing."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    msg_type = msg.get("type", "unknown")
    data = msg.get("data", {})
    
    if msg_type == "gpio":
        # GPIO data now contains all pins as a dict
        pins_data = []
        for pin_num, pin_info in sorted(data.items(), key=lambda x: int(x[0])):
            value = pin_info.get("value", "?")
            label = pin_info.get("label", "")
            label_str = f" ({label})" if label else ""
            pins_data.append(f"Pin {pin_num}{label_str}={value}")
        return f"[{timestamp}] GPIO: {', '.join(pins_data)}"
    
    elif msg_type == "wifi":
        ssid = data.get("ssid", "N/A")
        connected = data.get("connected", False)
        signal = data.get("signal_level_dbm", "N/A")
        return f"[{timestamp}] WiFi: {ssid} | Connected: {connected} | Signal: {signal} dBm"
    
    elif msg_type == "bluetooth":
        powered = data.get("powered", False)
        connected = data.get("connected", False)
        return f"[{timestamp}] Bluetooth: Powered: {powered} | Connected: {connected}"
    
    elif msg_type == "system":
        cpu = data.get("cpu_percent", "N/A")
        temp = data.get("cpu_temp_c", "N/A")
        disk = data.get("disk_used_percent", "N/A")
        return f"[{timestamp}] System: CPU: {cpu}% | Temp: {temp}°C | Disk: {disk}%"
    
    else:
        return f"[{timestamp}] {msg_type.upper()}: {json.dumps(data, indent=2)}"


async def subscribe(url: str = "ws://localhost:8000/ws", raw: bool = False):
    """Connect to the WebSocket endpoint and print all messages."""
    print(f"Connecting to {url}...")
    
    try:
        async with websockets.connect(url) as websocket:
            print(f"Connected! Listening for updates...\n")
            print("=" * 80)
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if raw:
                        # Print raw JSON with pretty formatting
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        print(f"[{timestamp}] {json.dumps(data, indent=2)}")
                    else:
                        formatted = format_message(data)
                        print(formatted)
                except json.JSONDecodeError:
                    print(f"[RAW] {message}")
                except Exception as e:
                    print(f"[ERROR] Failed to process message: {e}")
                    print(f"[RAW] {message}")
    
    except websockets.exceptions.WebSocketException as e:
        print(f"\n❌ WebSocket error: {e}")
        print("\nMake sure the server is running:")
        print("  uvicorn rpi_simple_debugger.app:app --reload")
    except KeyboardInterrupt:
        print("\n\n👋 Disconnecting...")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Subscribe to rpi-simple-debugger WebSocket updates"
    )
    parser.add_argument(
        "--url",
        default="ws://localhost:8000/ws",
        help="WebSocket URL (default: ws://localhost:8000/ws)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Server host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Show raw JSON output instead of formatted messages"
    )
    
    args = parser.parse_args()
    
    # Build URL from host/port if --url not explicitly provided
    if args.url == "ws://localhost:8000/ws" and (args.host != "localhost" or args.port != 8000):
        url = f"ws://{args.host}:{args.port}/ws"
    else:
        url = args.url
    
    asyncio.run(subscribe(url, raw=args.raw))


if __name__ == "__main__":
    main()
