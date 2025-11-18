from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from .config import DebuggerSettings, load_settings
from .gpio_monitor import AllGPIOStates, GPIOMonitor
from .network_monitor import BluetoothStatus, NetworkMonitor, WiFiStatus
from .system_monitor import SystemHealth, SystemMonitor


class ConnectionManager:
    def __init__(self) -> None:
        self.active: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        to_remove: List[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                to_remove.append(ws)
        for ws in to_remove:
            self.disconnect(ws)


def create_app(settings: DebuggerSettings | None = None) -> FastAPI:
    settings = settings or load_settings()

    app = FastAPI(title="rpi-simple-debugger", version="0.1.0")
    manager = ConnectionManager()

    loop = asyncio.get_event_loop()

    # Shared state for latest values (use simple dicts for beginner clarity).
    latest_state: Dict[str, Any] = {
        "gpio": {},
        "wifi": None,
        "bluetooth": None,
        "system": None,
    }

    async def push_update(kind: str, payload: Any) -> None:
        latest_state[kind] = payload
        await manager.broadcast({"type": kind, "data": payload})

    # Monitors
    gpio_monitor: GPIOMonitor | None = None
    if settings.gpio_enabled:
        # Default to all BCM pins that are generally safe inputs for Pi 3/4.
        default_pins = [2, 3, 4, 17, 18, 22, 23, 24, 25, 27]

        def on_gpio_update(all_states: AllGPIOStates) -> None:
            asyncio.run_coroutine_threadsafe(
                push_update("gpio", all_states.to_dict()),
                loop,
            )

        gpio_monitor = GPIOMonitor(
            pins=default_pins,
            label_map=settings.gpio_label_map,
            interval_s=settings.gpio_poll_interval_s,
            on_update=on_gpio_update,
        )

    def on_wifi(status: WiFiStatus) -> None:
        asyncio.run_coroutine_threadsafe(
            push_update("wifi", status.__dict__), loop
        )

    def on_bt(status: BluetoothStatus) -> None:
        asyncio.run_coroutine_threadsafe(
            push_update("bluetooth", status.__dict__), loop
        )

    def on_system(health: SystemHealth) -> None:
        asyncio.run_coroutine_threadsafe(
            push_update("system", health.__dict__), loop
        )

    network_monitor: NetworkMonitor | None = None
    if settings.wifi_enabled or settings.bluetooth_enabled:
        network_monitor = NetworkMonitor(
            interval_s=settings.network_poll_interval_s,
            on_wifi=on_wifi,
            on_bt=on_bt,
        )

    system_monitor: SystemMonitor | None = None
    if settings.system_health_enabled:
        system_monitor = SystemMonitor(
            interval_s=settings.system_poll_interval_s,
            on_update=on_system,
        )

    @app.on_event("startup")
    async def _startup() -> None:  # pragma: no cover - integration behavior
        if gpio_monitor is not None:
            gpio_monitor.start()
        if network_monitor is not None:
            network_monitor.start()
        if system_monitor is not None:
            system_monitor.start()

    @app.on_event("shutdown")
    async def _shutdown() -> None:  # pragma: no cover - integration behavior
        if gpio_monitor is not None:
            gpio_monitor.stop()
        if network_monitor is not None:
            network_monitor.stop()
        if system_monitor is not None:
            system_monitor.stop()

    @app.get("/status")
    async def get_status() -> JSONResponse:
        """Return the most recent snapshot for easy polling UIs."""

        return JSONResponse(latest_state)

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:  # pragma: no cover
        await manager.connect(websocket)
        
        # Send initial state of all monitors when client connects
        # This ensures clients immediately see current state
        if gpio_monitor is not None:
            all_gpio_states = gpio_monitor.get_all_states()
            gpio_data = AllGPIOStates(all_gpio_states).to_dict()
            await websocket.send_json({
                "type": "gpio",
                "data": gpio_data,
            })
        
        try:
            # For now, the client does not need to send anything.
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    return app
