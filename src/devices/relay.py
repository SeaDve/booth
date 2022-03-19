import RPi.GPIO as GPIO
from gi.repository import GLib


class Relay:
    _timeout_id = None

    def __init__(self, port: int):
        super().__init__()

        self._port = port

        GPIO.setup(self._port, GPIO.OUT)

        self.turn_off()

    def ephemeral_on(self, duration_millisecs: int) -> None:
        self.turn_on()
        self._timeout_id = GLib.timeout_add(duration_secs, self.turn_off)

    def turn_on(self) -> None:
        if self._timeout_id is not None:
            GLib.source_remove(self._timeout_id)

        GPIO.output(self._port, GPIO.LOW)

    def turn_off(self) -> None:
        GPIO.output(self._port, GPIO.HIGH)
        self._timeout_id = None
