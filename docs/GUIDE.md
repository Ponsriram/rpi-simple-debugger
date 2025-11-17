# rpi-simple-debugger: Complete Guide

This comprehensive guide covers everything you need to know about setting up, configuring, and using rpi-simple-debugger.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Server](#running-the-server)
5. [API Reference](#api-reference)
6. [Client Examples](#client-examples)
7. [GPIO Monitoring](#gpio-monitoring)
8. [Network Monitoring](#network-monitoring)
9. [System Health Monitoring](#system-health-monitoring)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Usage](#advanced-usage)
12. [Performance Tuning](#performance-tuning)

## Introduction

**rpi-simple-debugger** is a beginner-friendly debugging tool for Raspberry Pi that provides real-time monitoring of:

- **GPIO pins**: Digital input state changes
- **WiFi**: Connection status, signal strength, IP address
- **Bluetooth**: Power state and connection status
- **System health**: CPU temperature, CPU usage, disk usage

All data is exposed via a FastAPI REST API and WebSocket streaming, making it easy to build custom dashboards, monitoring tools, or integrate with other applications.

### Key Features

✅ **Zero hardware requirements** - Works with built-in Raspberry Pi features  
✅ **Real-time updates** - WebSocket streaming for instant notifications  
✅ **Safe defaults** - GPIO configured as inputs only  
✅ **Cross-platform development** - Gracefully handles non-Raspberry Pi environments  
✅ **Beginner-friendly** - Clear code with extensive comments  

## Installation

### On Raspberry Pi

#### Option 1: From PyPI (when published)

```bash
pip install rpi-simple-debugger
```

#### Option 2: From Source

```bash
# Install git if needed
sudo apt update
sudo apt install git python3-venv python3-pip

# Clone the repository
git clone https://github.com/Ponsriram/rpi-simple-debugger.git
cd rpi-simple-debugger

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package with Raspberry Pi dependencies
pip install -e .[raspberry]

# Install WebSocket support
pip install websockets
```

### On Development Machine (Non-Raspberry Pi)

The application can run on any Linux, macOS, or Windows machine for development. GPIO features will be disabled automatically.

```bash
# Clone the repository
git clone https://github.com/Ponsriram/rpi-simple-debugger.git
cd rpi-simple-debugger

# Create virtual environment
python3 -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install without Raspberry Pi dependencies
pip install -e .

# Install WebSocket support
pip install websockets
```

### Verifying Installation

```bash
# Check that the package is installed
python -c "import rpi_simple_debugger; print('Installation successful!')"

# View package version
python -c "import rpi_simple_debugger; print(rpi_simple_debugger.__version__)"
```

## Configuration

Configuration is **optional**. The application uses sensible defaults if no configuration file is provided.

### Configuration File

Create a file named `rpi_debugger_settings.json` in your project directory:

```json
{
  "gpio_enabled": true,
  "wifi_enabled": true,
  "bluetooth_enabled": true,
  "system_health_enabled": true,
  "gpio_poll_interval_s": 0.1,
  "network_poll_interval_s": 2.0,
  "system_poll_interval_s": 2.0,
  "gpio_labels": [
    { "pin": 17, "label": "Red LED" },
    { "pin": 18, "label": "Green LED" },
    { "pin": 27, "label": "Start Button" },
    { "pin": 22, "label": "Stop Button" }
  ]
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `gpio_enabled` | boolean | `true` | Enable/disable GPIO monitoring |
| `wifi_enabled` | boolean | `true` | Enable/disable WiFi monitoring |
| `bluetooth_enabled` | boolean | `true` | Enable/disable Bluetooth monitoring |
| `system_health_enabled` | boolean | `true` | Enable/disable system health monitoring |
| `gpio_poll_interval_s` | float | `0.1` | How often to check GPIO pins (seconds) |
| `network_poll_interval_s` | float | `2.0` | How often to check network status (seconds) |
| `system_poll_interval_s` | float | `2.0` | How often to check system health (seconds) |
| `gpio_labels` | array | `[]` | Human-readable labels for GPIO pins |

### Default GPIO Pins

If `gpio_enabled` is `true`, the following BCM pins are monitored by default:

**`2, 3, 4, 17, 18, 22, 23, 24, 25, 27`**

These pins are generally safe for use as inputs on Raspberry Pi 3/4 models without interfering with essential system functions.

### Custom Configuration Path

You can specify a custom configuration file path programmatically:

```python
from pathlib import Path
from rpi_simple_debugger.config import load_settings

settings = load_settings(Path("/path/to/custom_config.json"))
```

## Running the Server

### Basic Usage

Start the server on all network interfaces (accessible from other devices):

```bash
uvicorn rpi_simple_debugger.app:create_app --factory --host 0.0.0.0 --port 8000
```

### Development Mode

Run with auto-reload when code changes (for development):

```bash
uvicorn rpi_simple_debugger.app:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

### Localhost Only

Run on localhost only (not accessible from network):

```bash
uvicorn rpi_simple_debugger.app:create_app --factory --host 127.0.0.1 --port 8000
```

### Custom Port

Use a different port:

```bash
uvicorn rpi_simple_debugger.app:create_app --factory --host 0.0.0.0 --port 5000
```

### Background Process

Run as a background process:

```bash
nohup uvicorn rpi_simple_debugger.app:create_app --factory --host 0.0.0.0 --port 8000 > debugger.log 2>&1 &
```

### Systemd Service

For production, create a systemd service (`/etc/systemd/system/rpi-debugger.service`):

```ini
[Unit]
Description=Raspberry Pi Simple Debugger
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/rpi-simple-debugger
Environment="PATH=/home/pi/rpi-simple-debugger/.venv/bin"
ExecStart=/home/pi/rpi-simple-debugger/.venv/bin/uvicorn rpi_simple_debugger.app:create_app --factory --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable rpi-debugger
sudo systemctl start rpi-debugger
sudo systemctl status rpi-debugger
```

## API Reference

### REST Endpoints

#### GET /status

Returns the current state of all monitors.

**Request:**
```bash
curl http://localhost:8000/status
```

**Response:** `200 OK`
```json
{
  "gpio": {
    "17": {
      "pin": 17,
      "value": 1,
      "label": "Red LED"
    },
    "27": {
      "pin": 27,
      "value": 0,
      "label": "Start Button"
    }
  },
  "wifi": {
    "connected": true,
    "ssid": "MyNetwork",
    "ip_address": "192.168.1.42",
    "signal_level_dbm": -55
  },
  "bluetooth": {
    "powered": true,
    "connected": false
  },
  "system": {
    "cpu_temp_c": 52.3,
    "cpu_percent": 23.5,
    "disk_used_percent": 41.2
  }
}
```

**Notes:**
- The `gpio` object only contains pins that have changed state at least once
- All values represent the most recent reading from each monitor
- `null` values indicate data is unavailable

### WebSocket Endpoint

#### WS /ws

Establishes a persistent WebSocket connection for real-time updates.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(`Type: ${message.type}`, message.data);
};
```

**Message Format:**

All messages follow this structure:
```json
{
  "type": "gpio|wifi|bluetooth|system",
  "data": { ... }
}
```

See [API Reference in README](../README.md#websocket-endpoint) for detailed message formats.

## Client Examples

### Python WebSocket Client

The included `tests/ws_subscriber.py` provides a complete example:

```bash
# Pretty formatted output
python3 tests/ws_subscriber.py --host 192.168.1.42

# Raw JSON output
python3 tests/ws_subscriber.py --host 192.168.1.42 --raw

# Custom port
python3 tests/ws_subscriber.py --host 192.168.1.42 --port 5000
```

### JavaScript/Browser Client

```html
<!DOCTYPE html>
<html>
<head>
  <title>RPi Debugger Monitor</title>
</head>
<body>
  <div id="status"></div>

  <script>
    const ws = new WebSocket('ws://192.168.1.42:8000/ws');
    const statusDiv = document.getElementById('status');

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      
      if (msg.type === 'gpio') {
        console.log(`GPIO Pin ${msg.data.pin} (${msg.data.label}): ${msg.data.value}`);
      } else if (msg.type === 'wifi') {
        statusDiv.innerHTML = `WiFi: ${msg.data.ssid} (${msg.data.signal_level_dbm} dBm)`;
      } else if (msg.type === 'system') {
        console.log(`CPU: ${msg.data.cpu_percent}% | Temp: ${msg.data.cpu_temp_c}°C`);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };
  </script>
</body>
</html>
```

### Python REST Client

```python
import requests

# Get current status
response = requests.get('http://192.168.1.42:8000/status')
data = response.json()

print(f"WiFi SSID: {data['wifi']['ssid']}")
print(f"CPU Temp: {data['system']['cpu_temp_c']}°C")
print(f"GPIO Pins: {data['gpio']}")
```

### Node.js WebSocket Client

```javascript
const WebSocket = require('ws');

const ws = new WebSocket('ws://192.168.1.42:8000/ws');

ws.on('open', () => {
  console.log('Connected to RPi debugger');
});

ws.on('message', (data) => {
  const msg = JSON.parse(data);
  console.log(`[${msg.type}]`, msg.data);
});

ws.on('error', (error) => {
  console.error('Error:', error);
});
```

## GPIO Monitoring

### How It Works

The GPIO monitor:
1. Configures specified pins as inputs with BCM numbering
2. Polls each pin at the configured interval (default: 0.1s)
3. Detects state changes (0→1 or 1→0)
4. Broadcasts changes via WebSocket

### Pin Numbering

This project uses **BCM (Broadcom) pin numbering**, not physical pin numbers.

![BCM Pin Layout](https://pinout.xyz/resources/raspberry-pi-pinout.png)

### Adding Pin Labels

Labels make it easier to identify pins in your application:

```json
{
  "gpio_labels": [
    { "pin": 17, "label": "Door Sensor" },
    { "pin": 18, "label": "Motion Detector" },
    { "pin": 27, "label": "Emergency Stop" }
  ]
}
```

### Triggering GPIO Events

GPIO updates are sent **only when pin states change**. To test:

**Method 1: Jumper Wires**
- Connect a pin to 3.3V → value becomes `1`
- Connect a pin to GND → value becomes `0`
- Disconnect → value may float (unreliable without pull resistors)

**Method 2: Button/Switch**
- Connect button between pin and GND
- Enable internal pull-up in code (requires modification)
- Press button → value becomes `0`

**Method 3: External Circuit**
- Use sensors, switches, or other digital outputs
- Ensure voltage is 3.3V (NOT 5V - this can damage the Pi!)

### Safety Notes

⚠️ **Important GPIO Safety:**
- Never connect 5V directly to GPIO pins (use 3.3V max)
- Avoid connecting outputs from multiple sources to the same pin
- GPIO pins can source/sink ~16mA max
- Use current-limiting resistors when driving LEDs
- Be careful with pins used by system (I2C, SPI, etc.)

## Network Monitoring

### WiFi Monitoring

The WiFi monitor uses `iwconfig` to gather:
- Connection status
- SSID (network name)
- IP address
- Signal strength in dBm

**Signal Strength Guide:**
- `-30 to -50 dBm`: Excellent
- `-50 to -60 dBm`: Good
- `-60 to -70 dBm`: Fair
- `-70 to -80 dBm`: Weak
- `-80 to -90 dBm`: Very weak

### Bluetooth Monitoring

Monitors Bluetooth adapter status:
- Whether Bluetooth is powered on
- Whether any device is connected

**Note:** Detailed device information is not currently exposed to keep the API simple.

## System Health Monitoring

### CPU Temperature

- Reads from `psutil.sensors_temperatures()`
- On Raspberry Pi, typically from `cpu-thermal` sensor
- Returns `null` if unavailable
- Normal operating range: 30-80°C
- Consider cooling if consistently above 70°C

### CPU Usage

- Percentage of CPU time used (0-100%)
- Averaged across all cores
- Sampled at each polling interval

### Disk Usage

- Percentage of root filesystem used (0-100%)
- Based on `/` mount point
- Consider cleanup if above 90%

## Troubleshooting

### Server Won't Start

**Error: `Address already in use`**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
kill <PID>

# Or use a different port
uvicorn rpi_simple_debugger.app:create_app --factory --host 0.0.0.0 --port 8001
```

**Error: `ModuleNotFoundError: No module named 'rpi_simple_debugger'`**
```bash
# Ensure you're in the virtual environment
source .venv/bin/activate

# Reinstall the package
pip install -e .[raspberry]
```

### WebSocket Connection Fails

**Error: `WARNING: Unsupported upgrade request`**

This means WebSocket support is missing. Install it:
```bash
pip install websockets
```

**Connection refused from another device:**

Ensure:
1. Server is running on `0.0.0.0`, not `127.0.0.1`
2. Firewall allows port 8000
3. You're using the correct IP address

```bash
# Check Raspberry Pi's IP address
hostname -I

# Test from Pi itself
curl http://localhost:8000/status
```

### No GPIO Data

GPIO updates only occur when pins **change state**. To see data:
1. Connect a pin to 3.3V or GND
2. Use a button or switch
3. Check that GPIO is enabled in config

### Permission Errors (GPIO)

If you see GPIO permission errors:
```bash
# Add your user to the gpio group
sudo usermod -a -G gpio $USER

# Log out and back in for changes to take effect
```

### High CPU Usage

If the server uses too much CPU:
1. Increase polling intervals in configuration
2. Disable unnecessary monitors
3. Check for infinite loops in custom code

```json
{
  "gpio_poll_interval_s": 0.5,
  "network_poll_interval_s": 5.0,
  "system_poll_interval_s": 5.0
}
```

## Advanced Usage

### Custom FastAPI Integration

You can integrate rpi-simple-debugger into your own FastAPI application:

```python
from fastapi import FastAPI
from rpi_simple_debugger.app import create_app
from rpi_simple_debugger.config import DebuggerSettings

# Create main app
app = FastAPI(title="My Custom App")

# Create debugger app with custom settings
settings = DebuggerSettings(
    gpio_enabled=True,
    gpio_poll_interval_s=0.2,
)
debugger_app = create_app(settings)

# Mount debugger under /debugger prefix
app.mount("/debugger", debugger_app)

# Add your own routes
@app.get("/")
def read_root():
    return {"message": "My custom application"}
```

Access debugger at:
- `http://localhost:8000/debugger/status`
- `ws://localhost:8000/debugger/ws`

### Programmatic Usage

Use monitors directly in your Python code:

```python
import asyncio
from rpi_simple_debugger.gpio_monitor import GPIOMonitor, GPIOState

def handle_gpio_change(state: GPIOState):
    print(f"Pin {state.pin} changed to {state.value}")

# Create monitor
monitor = GPIOMonitor(
    pins=[17, 27],
    label_map={17: "LED", 27: "Button"},
    interval_s=0.1,
    on_change=handle_gpio_change,
)

# Start monitoring
monitor.start()

# Your application code here
try:
    while True:
        asyncio.sleep(1)
except KeyboardInterrupt:
    monitor.stop()
```

### Environment Variables

Override settings with environment variables:

```bash
export RPI_DEBUGGER_CONFIG=/path/to/config.json
uvicorn rpi_simple_debugger.app:create_app --factory --host 0.0.0.0 --port 8000
```

## Performance Tuning

### Optimizing for Your Use Case

**Low-latency GPIO monitoring:**
```json
{
  "gpio_poll_interval_s": 0.05,
  "network_poll_interval_s": 10.0,
  "system_poll_interval_s": 10.0
}
```

**Low CPU usage:**
```json
{
  "gpio_poll_interval_s": 1.0,
  "network_poll_interval_s": 30.0,
  "system_poll_interval_s": 30.0
}
```

**Battery-powered applications:**
- Increase all polling intervals
- Disable unnecessary monitors
- Consider event-driven GPIO instead of polling (requires code modification)

### Scaling Considerations

For multiple concurrent WebSocket clients:
- The server handles broadcasting to all connected clients
- Memory usage scales with number of connections
- Test with your expected number of clients
- Consider using a reverse proxy (nginx) for production

### Network Performance

Reduce WebSocket message frequency by:
- Increasing polling intervals
- Filtering data server-side
- Implementing client-side throttling

---

## Need Help?

- **Issues**: [GitHub Issues](https://github.com/Ponsriram/rpi-simple-debugger/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Ponsriram/rpi-simple-debugger/discussions)
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

Happy debugging! 🔧🍓
