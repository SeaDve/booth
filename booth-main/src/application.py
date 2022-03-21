from threading import Thread
from datetime import datetime
from typing import Union

from gi.repository import GLib

from camera import Camera
from person import Person, PersonParseError
from spreadsheet import Spreadsheet
from utils import log_error, log_info
from devices.proximity import ProximitySensor
from devices.temperature import TemperatureSensor
from devices.display import Display
from devices.relay import Relay

DEFAULT_CODE_DETECTED_TIMEOUT = 5  # seconds
DEFAULT_TEMPERATURE = -1
DEFAULT_SPREADSHEET_ID = "1IA6YhAdkvdNkkPPyhCj5JQrB8dcaKZNWzk-4gI0Ea4Y"

# GPIO ports
PROXIMITY_SENSOR_IO = 4
PUMP_IO = 17
BUZZER_IO = 24


class Application:
    _last_code: Union[str, None] = None
    _abnormal_temperature_handler = None

    _camera: Camera
    _display: Display
    _pump: Relay
    _buzzer: Relay
    _proximity_sensor: ProximitySensor
    _temperature_sensor: TemperatureSensor

    def __init__(self):
        self._proximity_sensor = ProximitySensor(PROXIMITY_SENSOR_IO)
        self._detected_handler_id = self._proximity_sensor.connect(
            "detected", self._on_proximity_sensor_detected
        )

        self._temperature_sensor = TemperatureSensor()

        try:
            self._display = Display([" Place QR Code  ", " ^ ^ Above ^ ^  "])
        except OSError as error:
            log_error(f"Failed to initialize display: {error}")

        self._pump = Relay(PUMP_IO, True)

        self._buzzer = Relay(BUZZER_IO)

        self._camera = Camera()
        self._camera.connect("error", lambda _: self._buzzer.ephemeral_on(5000))
        self._code_detected_handler_id = self._camera.connect(
            "code-detected", self._on_code_detected
        )

        try:
            self._camera.start()
        except Exception as error:
            log_error(f"Failed to start camera: {error}")
            self._buzzer.ephemeral_on(5000)

        GLib.timeout_add_seconds(5, self._reset_last_code)

        self._buzzer.ephemeral_on(50)

    def run(self):
        loop = GLib.MainLoop()

        try:
            loop.run()
        except KeyboardInterrupt:
            loop.quit()
        finally:
            self._display.clear()

    def _on_proximity_sensor_detected(self, proximity_sensor: ProximitySensor) -> None:
        log_info("Proximity sensor detected something")

        self._proximity_sensor.handler_block(self._detected_handler_id)

        self._pump.ephemeral_on(1500)
        temperature = self._temperature_sensor.get_object_temperature()
        self._check_abnormal_temperature(temperature)
        self._display.ephemeral_write(
            ["  Temperature:  ", f"     {temperature:.1f} C     "], 3
        )

        try:
            person = Person.from_str(
                f"""
name: Unknown
address: Unknown
contact_number: Unknown
room_id: Unknown
time_detected: {datetime.now().isoformat()}
temperature: {temperature}
"""
            )
            self._try_store_person_to_spreadsheet(person)
        except PersonParseError as error:
            self._handle_person_parse_error(error)

        self._proximity_sensor.handler_unblock(self._detected_handler_id)

    def _on_code_detected(self, camera: Camera, code: str) -> None:
        self._camera.handler_block(self._code_detected_handler_id)
        self._proximity_sensor.handler_block(self._detected_handler_id)

        if self._last_code == code:
            log_info("Same code as last; returning...")
        else:
            self._buzzer.ephemeral_on(500)
            self._handle_new_code_detected(code)

    def _store_person_to_spreadsheet_thread(self, person: Person) -> None:
        Spreadsheet(DEFAULT_SPREADSHEET_ID).append_person(person)

    def _try_store_person_to_spreadsheet(self, person: Person) -> None:
        try:
            thread = Thread(
                target=self._store_person_to_spreadsheet_thread, args=[person]
            )
            thread.run()
        except Exception as error:
            log_error(f"Failed to store person to spreadsheet: {error}")

    def _handle_proximity_sensor_wait_for_input(
        self, is_timeout_reached: bool, code: str
    ) -> None:
        temperature = DEFAULT_TEMPERATURE

        if is_timeout_reached:
            self._display.ephemeral_write(["   Received no  ", "  Temperature   "], 3)
            log_info(
                "Skipped dispensing alcohol and getting temperature: Timeout reached"
            )
        else:
            log_info(
                "Proximity sensor detected something. Dispensing alcohol and getting temp"
            )

            self._pump.ephemeral_on(1500)
            temperature = self._temperature_sensor.get_object_temperature()
            self._check_abnormal_temperature(temperature)
            self._display.ephemeral_write(
                ["  Temperature:  ", f"     {temperature:.1f} C     "], 3
            )

        try:
            person = Person.from_str(
                f"{code}\ntime_detected: {datetime.now().isoformat()}\ntemperature: {temperature}"
            )
            self._try_store_person_to_spreadsheet(person)
            self._display.ephemeral_write([person.name, "Hi, info logged "], 3)
        except PersonParseError as error:
            self._handle_person_parse_error(error)

        self._camera.handler_unblock(self._code_detected_handler_id)
        self._proximity_sensor.handler_unblock(self._detected_handler_id)

    def _handle_new_code_detected(self, code: str) -> None:
        log_info(f"New detected code `{code}`")

        self._last_code = code

        log_info(f"Waiting {DEFAULT_CODE_DETECTED_TIMEOUT} seconds for hand")
        self._display.write([" Put hand below ", "alchohol & temp "])
        self._proximity_sensor.wait_for_input(
            DEFAULT_CODE_DETECTED_TIMEOUT,
            self._handle_proximity_sensor_wait_for_input,
            code,
        )

    def _handle_person_parse_error(self, error: PersonParseError) -> None:
        self._buzzer.ephemeral_on(200)
        GLib.timeout_add(400, self._buzzer.ephemeral_on, 200)
        log_error(f"Failed parsing Person from string: {error}")

    def _check_abnormal_temperature(self, temp: float) -> None:
        if self._abnormal_temperature_handler is not None:
            GLib.source_remove(self._abnormal_temperature_handler)
            self._abnormal_temperature_handler = None

        def __inner():
            self._buzzer.ephemeral_on(1000)
            return True

        if temp > 38.0:
            self._abnormal_temperature_handler = GLib.timeout_add_seconds(2, __inner)

    def _reset_last_code(self):
        self._last_code = None
        return True
