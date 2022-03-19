import RPi.GPIO as GPIO
from gi.repository import GLib


class Relay:
    _timeout_id = None

    def __init__(self, port: int, reverse: bool = False):
        super().__init__()

        self._port = port
        self._reverse = reverse

        GPIO.setup(self._port, GPIO.OUT)

        self.turn_off()

    def ephemeral_on(self, duration_millisecs: int) -> None:
        self.turn_on()
        self._timeout_id = GLib.timeout_add(duration_millisecs, self.turn_off)

    def turn_on(self) -> None:
        if self._timeout_id is not None:
            GLib.source_remove(self._timeout_id)

        if self._reverse:
            GPIO.output(self._port, GPIO.LOW)
        else:
            GPIO.output(self._port, GPIO.HIGH)

    def turn_off(self) -> None:
        if self._reverse:
            GPIO.output(self._port, GPIO.HIGH)
        else:
            GPIO.output(self._port, GPIO.LOW)

        self._timeout_id = None
