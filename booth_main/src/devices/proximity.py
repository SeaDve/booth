from typing import Callable, Any

import RPi.GPIO as GPIO
from gi.repository import GObject, GLib


class ProximitySensor(GObject.Object):
    __gsignals__ = {"detected": (GObject.SIGNAL_RUN_LAST, None, ())}

    _detected_handler_id = None
    _timeout_handler_id = None

    def __init__(self, bcm_port: str):
        super().__init__()

        self._bcm_port = bcm_port

        GPIO.setup(self._bcm_port, GPIO.IN)
        GLib.timeout_add(250, self._check_for_input)

    def _check_for_input(self):
        if GPIO.input(self._bcm_port) == 0:
            self.emit("detected")
        return True

    def wait_for_input(
        self, timeout_secs: int, callback: Callable[[bool], None], *args: Any
    ) -> None:
        def callback_inner(is_timeout_reached: bool) -> bool:
            if self._detected_handler_id is not None:
                self.disconnect(self._detected_handler_id)
                self._detected_handler_id = None

            if self._timeout_handler_id is not None:
                GLib.source_remove(self._timeout_handler_id)
                self._timeout_handler_id = None

            callback(is_timeout_reached, *args)
            return False

        self._detected_handler_id = self.connect(
            "detected", lambda _: callback_inner(False)
        )
        self._timeout_handler_id = GLib.timeout_add_seconds(5, callback_inner, True)
