import time
from typing import Callable

import RPi.GPIO as GPIO
from gi.repository import GObject, GLib


class WaitForInputTimeout(Exception):
    def __init__(self, secs: int):
        self._timeout = secs

    def __str__(self):
        return f"Timeout of {self._timeout} is reached"


class ProximitySensor(GObject.Object):
    __gsignals__ = {"detected": (GObject.SIGNAL_RUN_LAST, None, ())}

    def __init__(self, bcm_port: str):
        super().__init__()

        self._bcm_port = bcm_port

        GPIO.setup(self._bcm_port, GPIO.IN)
        GLib.timeout_add(250, self._check_for_input)

    def _check_for_input(self):
        if GPIO.input(self._bcm_port) == 0:
            self.emit("detected")
        return True

    def wait_for_input(self, timeout_secs: int) -> None:
        while True:
            if self._time > (timeout_secs * 5):
                raise WaitForInputTimeout(timeout_secs)

            if GPIO.input(self._bcm_port) == 0:
                break

            self._time += 1
            time.sleep(0.2)
