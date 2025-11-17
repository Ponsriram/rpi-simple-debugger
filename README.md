# rpi-simple-debugger

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Beginner-friendly Raspberry Pi debugging helper.

This library exposes a small FastAPI application that streams:

- **GPIO** digital pin state changes
- **WiFi/Bluetooth** connection information
- **System health** (CPU temperature, CPU usage, disk usage)

The data is sent over WebSockets so any UI (web dashboard, Tkinter/PyQt tool, or another process) can subscribe and visualize it in real-time.

## Installation

**On your Raspberry Pi (recommended):**

```bash
pip install rpi-simple-debugger
```

**For development in this repo:**

```bash
# Clone the repository
git clone https://github.com/Ponsriram/rpi-simple-debugger.git
cd rpi-simple-debugger

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with Raspberry Pi dependencies
pip install -e .[raspberry]

# Install WebSocket support for uvicorn
pip install websockets
```

## Quick Start

**1. Create a settings file (optional):**

```jsonc
// rpi_debugger_settings.json
{
  "gpio_enabled": true,
  "wifi_enabled": true,
  "bluetooth_enabled": true,
  "system_health_enabled": true,
  "gpio_poll_interval_s": 0.1,
  "network_poll_interval_s": 2.0,
  "system_poll_interval_s": 2.0,
  "gpio_labels": [
    { "pin": 17, "label": "LED" },
    { "pin": 27, "label": "Button" }
  ]
}
```

**2. Run the server:**

```bash
uvicorn rpi_simple_debugger.app:create_app --factory --host 0.0.0.0 --port 8000
```

**3. Connect to the API:**

- **WebSocket:** `ws://<pi-address>:8000/ws` for live updates
- **REST API:** `http://<pi-address>:8000/status` for the latest snapshot

## API Reference

### REST Endpoints

#### `GET /status`

Returns the most recent snapshot of all monitoring data.

**Response Format:**

```json
{
  "gpio": {
    "17": {
      "pin": 17,
      "value": 1,
      "label": "LED"
    },
    "27": {
      "pin": 27,
      "value": 0,
      "label": "Button"
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

**Field Descriptions:**

- `gpio`: Object containing the latest state of each monitored GPIO pin (only pins that have changed at least once)
- `wifi`: Latest WiFi connection status
- `bluetooth`: Latest Bluetooth status
- `system`: Latest system health metrics

### WebSocket Endpoint

#### `WS /ws`

Establishes a WebSocket connection that broadcasts real-time updates whenever monitored values change.

**Message Types:**

All WebSocket messages follow this structure:
```json
{
  "type": "<message_type>",
  "data": { ... }
}
```

#### GPIO Update

Sent whenever a GPIO pin changes state (0→1 or 1→0).

```json
{
  "type": "gpio",
  "data": {
    "pin": 17,
    "value": 1,
    "label": "LED"
  }
}
```

**Fields:**
- `pin` (integer): BCM pin number
- `value` (integer): Current pin state (0 = LOW, 1 = HIGH)
- `label` (string|null): Human-readable label from configuration, or `null` if not set

**Note:** GPIO updates are only sent when pin states change. Connect a button, switch, or wire to trigger updates.

#### WiFi Update

Sent periodically (default: every 2 seconds) with WiFi connection status.

```json
{
  "type": "wifi",
  "data": {
    "connected": true,
    "ssid": "MyNetwork",
    "ip_address": "192.168.1.42",
    "signal_level_dbm": -67
  }
}
```

**Fields:**
- `connected` (boolean): Whether WiFi is currently connected
- `ssid` (string|null): Network name, or `null` if disconnected
- `ip_address` (string|null): Current IP address, or `null` if disconnected
- `signal_level_dbm` (integer|null): Signal strength in dBm (typically -30 to -90), or `null` if unavailable

#### Bluetooth Update

Sent periodically (default: every 2 seconds) with Bluetooth status.

```json
{
  "type": "bluetooth",
  "data": {
    "powered": true,
    "connected": false
  }
}
```

**Fields:**
- `powered` (boolean): Whether Bluetooth adapter is powered on
- `connected` (boolean): Whether any Bluetooth device is currently connected

#### System Health Update

Sent periodically (default: every 2 seconds) with system health metrics.

```json
{
  "type": "system",
  "data": {
    "cpu_temp_c": 47.2,
    "cpu_percent": 6.6,
    "disk_used_percent": 18.8
  }
}
```

**Fields:**
- `cpu_temp_c` (float|null): CPU temperature in Celsius, or `null` if unavailable
- `cpu_percent` (float): CPU usage percentage (0-100)
- `disk_used_percent` (float): Disk usage percentage (0-100)

## Example Client

A WebSocket subscriber client is included in `tests/ws_subscriber.py`:

```bash
# View formatted output
python3 tests/ws_subscriber.py --host <pi-address>

# View raw JSON output
python3 tests/ws_subscriber.py --host <pi-address> --raw
```

## Configuration

All configuration is optional. If no `rpi_debugger_settings.json` file is present, the application uses sensible defaults.

**Configuration Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `gpio_enabled` | boolean | `true` | Enable GPIO monitoring |
| `wifi_enabled` | boolean | `true` | Enable WiFi monitoring |
| `bluetooth_enabled` | boolean | `true` | Enable Bluetooth monitoring |
| `system_health_enabled` | boolean | `true` | Enable system health monitoring |
| `gpio_poll_interval_s` | float | `0.1` | GPIO polling interval in seconds |
| `network_poll_interval_s` | float | `2.0` | Network polling interval in seconds |
| `system_poll_interval_s` | float | `2.0` | System health polling interval in seconds |
| `gpio_labels` | array | `[]` | Array of pin labels: `[{"pin": 17, "label": "LED"}]` |

**Default Monitored GPIO Pins (BCM numbering):**
`2, 3, 4, 17, 18, 22, 23, 24, 25, 27`

These are generally safe input pins on Raspberry Pi 3/4 models.

## Design Goals

- **No custom hardware required** – uses on-board peripherals only
- **Safe defaults** – GPIO configured as inputs only, graceful failure on non-Raspberry Pi machines
- **Minimal configuration** – single optional JSON file
- **Clear, commented code** – intended for learners and educators
- **Build any UI** – FastAPI backend works with any frontend framework

## Documentation

- [Full Guide](docs/GUIDE.md) - Comprehensive setup and usage guide
- [Contributing](CONTRIBUTING.md) - How to contribute to this project
- [License](LICENSE) - MIT License

## Requirements

- Python 3.9+
- Raspberry Pi OS (or any Linux distribution for development)
- FastAPI 0.115.0+
- uvicorn 0.30.0+
- pydantic 2.7.0+
- psutil 6.0.0+
- RPi.GPIO 0.7.0+ (Raspberry Pi only)
- websockets (for WebSocket support)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
