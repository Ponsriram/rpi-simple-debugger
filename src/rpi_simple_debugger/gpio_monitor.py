from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

try:  # Optional on non-RPi platforms
    import RPi.GPIO as GPIO  # type: ignore[import]
except Exception:  # pragma: no cover - not available on dev machines
    GPIO = None  # type: ignore[assignment]


@dataclass
class GPIOState:
    pin: int
    value: int
    label: Optional[str]


@dataclass
class AllGPIOStates:
    """Container for all GPIO pin states."""
    pins: Dict[int, Dict[str, Any]]  # pin_number -> {pin, value, label}
    
    def __init__(self, states: List[GPIOState]):
        self.pins = {
            state.pin: {
                "pin": state.pin,
                "value": state.value,
                "label": state.label,
            }
            for state in states
        }

    def to_dict(self) -> Dict[int, Dict[str, Any]]:
        return self.pins


class GPIOMonitor:
    """Polls GPIO pins and reports complete state periodically.

    This uses simple polling instead of interrupts so it behaves
    consistently across boards and is easier to explain to beginners.
    
    Similar to WiFi, Bluetooth, and System monitors, this sends the
    complete state of all pins at each polling interval.
    """

    def __init__(
        self,
        pins: List[int],
        label_map: Dict[int, str],
        interval_s: float,
        on_update: Callable[[AllGPIOStates], None],
    ) -> None:
        self._pins = pins
        self._label_map = label_map
        self._interval_s = interval_s
        self._on_update = on_update
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._last_values: Dict[int, int] = {}

    def start(self) -> None:
        if GPIO is None:
            # Library can still run; GPIO data will just be absent.
            return

        if self._thread and self._thread.is_alive():
            return

        GPIO.setmode(GPIO.BCM)
        for pin in self._pins:
            GPIO.setup(pin, GPIO.IN)

        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
        if GPIO is not None:
            GPIO.cleanup()

    def get_all_states(self) -> List[GPIOState]:
        """Get the current state of all monitored pins.
        
        Returns:
            List of GPIOState objects for all monitored pins.
        """
        states = []
        for pin in self._pins:
            value = self._last_values.get(pin, 0)
            states.append(
                GPIOState(
                    pin=pin,
                    value=value,
                    label=self._label_map.get(pin),
                )
            )
        return states

    def _loop(self) -> None:
        while not self._stop.is_set():
            # Read all pins and update last values
            for pin in self._pins:
                value = GPIO.input(pin) if GPIO is not None else 0
                self._last_values[pin] = int(value)
            
            # Send complete state update (like WiFi/Bluetooth/System monitors)
            all_states = self.get_all_states()
            self._on_update(AllGPIOStates(all_states))
            
            time.sleep(self._interval_s)
